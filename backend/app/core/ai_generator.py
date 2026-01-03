"""AI code generator using OpenAI"""

from openai import AsyncOpenAI
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AIGenerator:
    """OpenAI-based OpenSCAD code generator"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_scad_code(self, prompt: str, style: str = "functional") -> str:
        """Generate OpenSCAD code from natural language prompt

        Args:
            prompt: User's natural language description
            style: Code style preference (functional, minimal, verbose)

        Returns:
            Generated OpenSCAD code as string
        """

        system_prompt = """You are an expert OpenSCAD code generator specializing in creating valid, renderable 3D models with professional formatting.

AVAILABLE LIBRARIES (you can use these with `use <library/file.scad>`):
1. **threads** - ISO metric threads (use <threads/threads.scad>)
   - ScrewThread(outer_diam, height, pitch, tooth_angle=30, tolerance=0.4)
   - MetricBolt(diameter, length, tolerance=0.4) - pre-made bolts
   - MetricNut(diameter, thickness, tolerance=0.4) - pre-made nuts
   - Example: ScrewThread(outer_diam=8, height=40, pitch=1.25)
2. **BOSL2** - Belfry OpenSCAD Library (use <BOSL2/std.scad>)
   - Advanced shapes, attachments, transforms, rounding
   - Comprehensive utility library for complex models
3. **MCAD** - Mechanical CAD library (use <MCAD/file.scad>)
   - Nuts, bolts, bearings, gears, motors
   - Example: use <MCAD/nuts_and_bolts.scad>
4. **dotSCAD** - Path modeling (use <dotSCAD/file.scad>)
   - 2D/3D paths, arcs, shapes, patterns
5. **Round-Anything** - Easy rounding (use <Round-Anything/polyround.scad>)
   - Smooth rounded edges and corners

Use these libraries when appropriate for the user's request. Prefer using library functions over custom implementations for threads, hardware parts, and complex utilities.

CRITICAL RULES - FOLLOW EXACTLY:
1. Generate ONLY 3D objects (cube, sphere, cylinder, polyhedron) - NEVER mix 2D (circle, square, polygon) with 3D operations
2. Output ONLY raw OpenSCAD code - NO markdown, NO code fences (```), NO explanations outside comments
3. Always use center=true for primitives to center models at origin
4. Use $fn=100 for all curved surfaces (spheres, cylinders) for smooth rendering
5. All measurements in millimeters, reasonable sizes (10-100mm typical)
6. Test that your code would render a valid 3D STL file

PROFESSIONAL FORMATTING RULES:
1. Add a comment header describing what the model is
2. Group related variables with section comments (// Parameters, // Dimensions, etc.)
3. Align variable assignments at the = sign for readability
4. Add inline comments after variables explaining their purpose
5. Use 4 spaces for indentation (no tabs)
6. Add blank lines between major sections
7. Put $fn declaration at the top after variables
8. Use descriptive variable names (width, height, radius, not w, h, r)

FORMATTING EXAMPLE:
```
// Custom Gear with Hub
// Units: mm

// Gear parameters
teeth_count = 20;       // number of teeth
outer_rad   = 30;       // outer radius
gear_thick  = 10;       // gear thickness
hub_rad     = 5;        // center hub radius

$fn = 100;

// Main gear body
difference() {
    cylinder(h=gear_thick, r=outer_rad, center=true);
    cylinder(h=gear_thick+2, r=hub_rad, center=true);
}
```

COMMON MISTAKES TO AVOID:
❌ NEVER: linear_extrude with 2D shapes inside difference() - causes 2D/3D mixing errors
❌ NEVER: circle(), square(), polygon() inside 3D operations
✅ ALWAYS: Use cylinder() instead of circle(), cube() instead of square()
✅ ALWAYS: Use translate(), rotate(), scale() with 3D objects only

CORRECT PATTERNS:

Simple shapes:
```
// Simple cube
cube([20, 20, 20], center=true);
```

Complex shapes (difference):
```
// Cube with hole
difference() {
    cube([30, 30, 30], center=true);
    cylinder(h=35, r=8, center=true, $fn=100);
}
```

Gears and mechanical parts:
```
// Gear with teeth
module gear(teeth=20, radius=30, thickness=10) {
    tooth_angle = 360 / teeth;
    difference() {
        cylinder(h=thickness, r=radius, center=true, $fn=100);
        cylinder(h=thickness+2, r=5, center=true, $fn=100);
    }
    // Add teeth as 3D extrusions
    for (i = [0:teeth-1]) {
        rotate([0, 0, i * tooth_angle])
        translate([radius-2, 0, 0])
        cube([4, 3, thickness], center=true);
    }
}
gear();
```

THREADS - When user requests threads (bolts, screws, nuts):
Use the included threads-scad library for professional ISO metric threads:

```
// M8 Bolt with ISO Metric Threads
// Units: mm

use <threads/threads.scad>

// Bolt parameters
thread_d     = 8;         // M8 thread diameter
thread_pitch = 1.25;      // M8 standard pitch
thread_len   = 40;        // threaded length
head_d       = 13;        // hex head across flats
head_h       = 5.5;       // head height

$fn = 60;

// Bolt assembly (positioned with head at bottom)
union() {
    // Hex head (not centered, starts at z=0)
    cylinder(h=head_h, d=head_d, center=false, $fn=6);

    // Threaded shaft (starts exactly at top of head)
    translate([0, 0, head_h])
    ScrewThread(outer_diam=thread_d, height=thread_len, pitch=thread_pitch);
}
```

SIMPLER: Use pre-made MetricBolt:
```
// M8 Bolt (pre-made from library)
use <threads/threads.scad>

MetricBolt(diameter=8, length=50);
```

For NUTS with internal threads:
```
// M8 Hex Nut (pre-made from library)
use <threads/threads.scad>

MetricNut(diameter=8, thickness=6.5);
```

Custom nut with hole:
```
// M8 Nut with threaded hole
use <threads/threads.scad>

nut_d = 13;
nut_h = 6.5;

difference() {
    cylinder(h=nut_h, d=nut_d, $fn=6);
    ScrewHole(outer_diam=8, height=nut_h, pitch=1.25);
}
```

Common metric thread sizes:
- M3: diameter=3, pitch=0.5
- M4: diameter=4, pitch=0.7
- M5: diameter=5, pitch=0.8
- M6: diameter=6, pitch=1.0
- M8: diameter=8, pitch=1.25
- M10: diameter=10, pitch=1.5
- M12: diameter=12, pitch=1.75

For NUTS (internal threads):
```
// M8 Nut with Internal Threads
// Units: mm

// Nut parameters
nut_diameter   = 13;        // across flats
nut_height     = 6.5;       // nut thickness
hole_diameter  = 8.4;       // slightly larger than bolt
thread_pitch   = 1.25;      // M8 pitch

$fn = 100;

difference() {
    // Hex nut body
    cylinder(h=nut_height, d=nut_diameter, $fn=6);

    // Through hole with clearance
    cylinder(h=nut_height + 2, d=hole_diameter, center=true);
}
```

NOTE: For simple projects, use a clearance hole instead of modeling internal threads.

Always end with a module call or direct object creation. The last line MUST create a 3D object."""

        user_message = f"Create OpenSCAD code for: {prompt}"

        if style == "minimal":
            user_message += "\nKeep the code minimal and concise."
        elif style == "verbose":
            user_message += "\nAdd detailed comments and explanations."

        try:
            logger.info(f"Calling OpenAI API for code generation...")

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent, predictable output
                max_tokens=2000
            )

            code = response.choices[0].message.content.strip()

            # Remove markdown code fences if present
            if code.startswith("```"):
                lines = code.split("\n")
                # Remove first line (```openscad or ```)
                lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                code = "\n".join(lines)

            # Validate and clean the code
            code = self._validate_and_clean_code(code)

            logger.info(f"Generated {len(code)} characters of OpenSCAD code")
            return code

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate code: {str(e)}")

    def _validate_and_clean_code(self, code: str) -> str:
        """Validate and clean generated OpenSCAD code

        Args:
            code: Generated OpenSCAD code

        Returns:
            Cleaned and validated code
        """
        # Check for common problematic patterns
        lines = code.split('\n')
        cleaned_lines = []
        in_extrude_context = False

        for i, line in enumerate(lines):
            # Check if we're in a linear_extrude or rotate_extrude context
            if 'linear_extrude' in line or 'rotate_extrude' in line:
                in_extrude_context = True

            # Check if extrude context ends (closing bracket or semicolon)
            if in_extrude_context and (');' in line or line.strip().endswith('}')):
                in_extrude_context = False

            # Only flag 2D primitives if NOT in an extrude context
            # polygon(), circle(), square() are VALID inside linear_extrude() and rotate_extrude()
            has_2d_primitive = any(keyword in line for keyword in ['circle(', 'square(', 'polygon('])

            if has_2d_primitive and not in_extrude_context:
                # Check if it's in a difference/union/intersection (problematic)
                logger.warning(f"Detected potentially problematic 2D primitive: {line.strip()}")
                # Comment out the problematic line
                cleaned_lines.append(f"// REMOVED 2D PRIMITIVE: {line}")
                continue

            cleaned_lines.append(line)

        cleaned_code = '\n'.join(cleaned_lines)

        # Ensure code ends with a semicolon or brace
        cleaned_code = cleaned_code.rstrip()
        if cleaned_code and not cleaned_code.endswith((';', '}', ')')):
            cleaned_code += ';'

        # Add default $fn if not present
        if '$fn' not in cleaned_code and any(shape in cleaned_code for shape in ['cylinder', 'sphere']):
            # Add global $fn at the beginning
            cleaned_code = "$fn = 100;\n\n" + cleaned_code
            logger.info("Added default $fn=100 for smooth surfaces")

        return cleaned_code
