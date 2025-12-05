FROM envoyproxy/envoy:distroless-v1.36.2

USER 60577:60577
EXPOSE 8443

CMD ["envoy", "-c", "/etc/envoy/envoy.yaml"]
