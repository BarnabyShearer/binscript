FROM python AS py
COPY elf.py bs.py bs.bs ./
RUN ./bs.py bs.bs bs

FROM scratch AS bs
COPY --from=py bs /
COPY greet.bs /
RUN ["./bs", "greet.bs", "greet"]

FROM scratch
COPY --from=bs greet /
ENTRYPOINT ["./greet"]
