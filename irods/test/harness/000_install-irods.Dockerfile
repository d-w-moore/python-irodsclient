FROM ubuntu:18.04
COPY install.sh /
RUN for phase in initialize install-essential-packages add-package-repo; do \
        bash /install.sh --w=$phase 0; \
    done
RUN /install.sh 4
COPY start_postgresql_and_irods.sh /
CMD bash /start_postgresql_and_irods.sh
