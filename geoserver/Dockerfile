FROM terrestris/geoserver:latest

ARG GS_DATA_PATH=./geoserver_data/
ARG CUSTOM_WEB_XML_PATH=./custom_web_xml/
ARG ADDITIONAL_LIBS_PATH=./additional_libs/

# remove default geoserver data
RUN rm -rf $GEOSERVER_DATA_DIR/*

COPY $GS_DATA_PATH $GEOSERVER_DATA_DIR
COPY $ADDITIONAL_LIBS_PATH $GEOSERVER_LIB_DIR
COPY $CUSTOM_WEB_XML_PATH $GEOSERVER_LIB_DIR/..

ENTRYPOINT /opt/startup.sh