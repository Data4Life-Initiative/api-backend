FROM jboss/keycloak:5.0.0

ADD ./resources/docker/iam/development/realm-export.json /opt/jboss/keycloak/

ENTRYPOINT [ "/opt/jboss/tools/docker-entrypoint.sh" ]

CMD ["-b", "0.0.0.0", "-Dkeycloak.import=/opt/jboss/keycloak/realm-export.json", "-Dkeycloak.migration.strategy=IGNORE_EXISTING"]
