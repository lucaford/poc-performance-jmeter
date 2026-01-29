FROM eclipse-temurin:11-jre

# Variables de entorno para JMeter
ENV JMETER_VERSION=5.6.3
ENV JMETER_HOME=/opt/jmeter
ENV PATH=${JMETER_HOME}/bin:${PATH}

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar JMeter
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz \
    && tar -xzf apache-jmeter-${JMETER_VERSION}.tgz \
    && mv apache-jmeter-${JMETER_VERSION} ${JMETER_HOME} \
    && rm apache-jmeter-${JMETER_VERSION}.tgz

# Crear directorios de trabajo
WORKDIR /jmeter

# Configurar entrypoint
ENTRYPOINT ["jmeter"]

