# AWS Emulator image for local runs (macOS/Windows have no native package; no prebuilt image is published).
# Based on the documented Dockerfile from the aws-emulator agent skill (.claude/skills/aws-emulator/references/container.md).
# Built by `make emulator-install`; rebuilt with --pull --no-cache to pick up the latest release.
FROM public.ecr.aws/amazonlinux/amazonlinux:2023-minimal
ARG TARGETARCH
RUN case "$TARGETARCH" in arm64) a=aarch64 ;; amd64) a=x86_64 ;; *) exit 1 ;; esac \
    && curl -fsSLo /tmp/aws-emulator.rpm \
       "https://downloads.aws.com/aws-emulator/packages/aws-emulator/LTS/latest/aws-emulator-$a.rpm" \
    && rpm -i /tmp/aws-emulator.rpm && rm /tmp/aws-emulator.rpm \
    && mkdir -p /home/emulator && chown 1000 /home/emulator
USER 1000
ENV HOME=/home/emulator
ENV PATH=/opt/aws-emulator/bin:$PATH
EXPOSE 9297
# -t off: telemetry off. Per `aws-emulator --help`, "off always wins over EMULATOR_TELEMETRY and the config file,
# on cannot override them", so every container from this image runs with telemetry off no matter how it's started.
ENTRYPOINT ["aws-emulator", "-b", "0.0.0.0", "-t", "off"]
