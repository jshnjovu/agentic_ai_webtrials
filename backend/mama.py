from googleapiclient.discovery import build

def main():
    # Specify your API key
    api_key = 'lala'  # Replace with your actual API key

    # Create the service using the API key
    service = build('pagespeedonline', 'v5', developerKey=api_key)

    # Specify the URL to analyze
    url = 'https://www.example.com'  # Replace with the URL you want to analyze

    # Call the PageSpeed Insights API
    response = service.pagespeedapi().runpagespeed(url=url).execute()

    # Print the JSON response
    print(response)

if __name__ == '__main__':
    main()
