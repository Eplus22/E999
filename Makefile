tex:
	cd MdFiles && python3 md2tex.py
clean:
	@rm -f preamble*
	@cd CheatSheets && rm -f mdtoch.py
	@rm -f run.sh
	@rm -f contentGen.py
	@cd MdFiles && rm -f md2tex.py
