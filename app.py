# from flask import Flask, render_template, request
# import requests
# from bs4 import BeautifulSoup

# app = Flask(__name__)

# def scrape_jobs(job_title):
#     # Format job title for URL, e.g., "python developer" -> "python+developer"
#     query = job_title.replace(' ', '+')

#     # Example site: RemoteOK (remote job board)
#     url = f"https://remoteok.io/remote-{query}-jobs"

#     headers = {
#         'User-Agent': 'Mozilla/5.0'
#     }

#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     jobs = []
#     # Find all job listings
#     # RemoteOK jobs are inside <tr class="job"> elements
#     job_rows = soup.find_all('tr', class_='job')

#     for job in job_rows[:10]:  # Limit to first 10 jobs
#         title_tag = job.find('h2', itemprop='title')
#         company_tag = job.find('h3', itemprop='name')
#         link_tag = job.find('a', class_='preventLink')

#         if title_tag and company_tag and link_tag:
#             title = title_tag.text.strip()
#             company = company_tag.text.strip()
#             link = "https://remoteok.io" + link_tag['href']

#             jobs.append({
#                 'title': title,
#                 'company': company,
#                 'link': link
#             })

#     return jobs

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     jobs = []
#     if request.method == 'POST':
#         job_title = request.form.get('job_title')
#         if job_title:
#             jobs = scrape_jobs(job_title)
#     return render_template('index.html', jobs=jobs)

# if __name__ == '__main__':
#     app.run(debug=True)





from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_remoteok(job_title):
    query = job_title.replace(' ', '+')
    url = f"https://remoteok.io/remote-{query}-jobs"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    rows = soup.find_all('tr', class_='job')
    for job in rows[:15]:
        title = job.find('h2', itemprop='title')
        company = job.find('h3', itemprop='name')
        location = job.find('div', class_='location')
        tags = job.find_all('div', class_='tag')
        date = job.find('time')

        link_tag = job.find('a', class_='preventLink')
        if title and company and link_tag:
            jobs.append({
                'title': title.text.strip(),
                'company': company.text.strip(),
                'location': location.text.strip() if location else 'Remote',
                'skills': [tag.text.strip() for tag in tags],
                'date_posted': date['datetime'] if date else 'N/A',
                'link': "https://remoteok.io" + link_tag['href'],
                'source': 'RemoteOK'
            })
    return jobs

def scrape_weworkremotely(job_title):
    query = job_title.lower().replace(' ', '-')
    url = f"https://weworkremotely.com/remote-jobs/search?term={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    jobs_section = soup.find('section', {'class': 'jobs'})
    if not jobs_section:
        return jobs

    listings = jobs_section.find_all('li', class_='feature') + jobs_section.find_all('li', class_='')

    for job in listings[:15]:
        company = job.find('span', class_='company')
        title = job.find('span', class_='title')
        region = job.find('span', class_='region company')
        link_tag = job.find('a', href=True)

        if title and company and link_tag:
            link = "https://weworkremotely.com" + link_tag['href']
            jobs.append({
                'title': title.text.strip(),
                'company': company.text.strip(),
                'location': region.text.strip() if region else 'Remote',
                'skills': [],  # WeWorkRemotely doesn't show skills tags on search page
                'date_posted': 'N/A',  # Date is not readily available here
                'link': link,
                'source': 'We Work Remotely'
            })
    return jobs

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        sites = request.form.getlist('sites')

        if job_title:
            if 'remoteok' in sites:
                jobs += scrape_remoteok(job_title)
            if 'weworkremotely' in sites:
                jobs += scrape_weworkremotely(job_title)

    return render_template('index.html', jobs=jobs)

if __name__ == '__main__':
    app.run(debug=True)

