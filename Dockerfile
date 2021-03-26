FROM python as py
COPY elf.py bs.py greet.bs ./
RUN ./bs.py greet.bs greet

FROM scratch
COPY --from=py greet /

ENTRYPOINT ["./greet"]
