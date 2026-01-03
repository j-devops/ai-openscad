FROM debian:bookworm-slim

# Install OpenSCAD, Python, and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openscad \
        python3 \
        python3-pip \
        xvfb \
        xauth \
        git \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install OpenSCAD libraries
RUN mkdir -p /usr/share/openscad/libraries && \
    cd /usr/share/openscad/libraries && \
    git clone --depth 1 https://github.com/rcolyer/threads-scad.git threads && \
    git clone --depth 1 https://github.com/BelfrySCAD/BOSL2.git BOSL2 && \
    git clone --depth 1 https://github.com/openscad/MCAD.git MCAD && \
    git clone --depth 1 https://github.com/JustinSDK/dotSCAD.git dotSCAD && \
    git clone --depth 1 https://github.com/Irev-Dev/Round-Anything.git Round-Anything && \
    echo "OpenSCAD libraries installed: threads, BOSL2, MCAD, dotSCAD, Round-Anything"

# Set OpenSCAD library path
ENV OPENSCADPATH=/usr/share/openscad/libraries

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create data directories
RUN mkdir -p /app/data/scad_files /app/data/renders /app/data/exports

# Expose port
EXPOSE 8002

# Run the queue processor
CMD ["python3", "-m", "app.main"]
