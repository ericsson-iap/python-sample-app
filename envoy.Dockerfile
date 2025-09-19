FROM envoyproxy/envoy:distroless-v1.35.0

USER 60577:60577
EXPOSE 8080 8443

CMD ["envoy", "-c", "/etc/envoy/envoy.yaml"]
