import requests
import time
import threading

URL = "http://localhost:5000/"  # Změňte podle potřeby
THREADS = 10
REQUESTS_PER_THREAD = 50

def worker(thread_id):
    for i in range(REQUESTS_PER_THREAD):
        try:
            start = time.time()
            r = requests.get(URL)
            elapsed = time.time() - start
            print(f"[Thread {thread_id}] Request {i+1}: {r.status_code} in {elapsed:.3f}s")
        except Exception as e:
            print(f"[Thread {thread_id}] Request {i+1}: ERROR {e}")

def main():
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(i+1,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("Performance test completed.")

if __name__ == "__main__":
    main()
