from src.jobs.ex_arbitrage_jobs.multi_api_job import main_job_multi_api
from src.jobs.ex_arbitrage_jobs.simple_job import main_job


if __name__ == "__main__":
    main_job()
    # Comment th above line and comment the below line to run the multi_api_job for multiple APIs
    # main_job_multi_api()
