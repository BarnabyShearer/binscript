bs: bs.bs bs.py
	./bs.py "$<" "$@"
%: %.bs bs
	./bs "$<" "$@"
