ifeq ($(HOST),)
HOST := localhost
endif

ifeq ($(PORT),)
PORT := 163
endif

server:
	python3 ./server.py $(PORT)

setup:
	pip install pyuv

event:
	python3 ./client_event.py $(HOST) $(PORT)

client:
	python3 ./client_thread.py $(HOST) $(PORT)

test-loss:
	@echo Loss over Complete Server-Client Session...
	python3 ./server.py $(PORT) & python3 ./client_thread.py localhost $(PORT) < ./Test/Dostoyevsky.txt
	pkill ./server.py

	@echo "Loss over Test Server-Client Session...\n"
	python3 ./Test/test_server.py $(PORT) & python3 ./Test/test_client.py localhost $(PORT) < ./Test/Dostoyevsky.txt
	pkill ./test_server.py
