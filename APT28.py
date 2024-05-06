import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_all_apt28_samples(api_key, limit_per_page=100, total_entries=10000):
    url = "https://mb-api.abuse.ch/api/v1/"
    
    all_samples = []
    page = 1

    while len(all_samples) < total_entries:
        data = {
            'query': 'get_taginfo',
            'tag': 'APT28',
            'limit': min(limit_per_page, total_entries - len(all_samples)),
            'page': page,
        }

        headers = {'API-KEY': api_key}

        try:
            response = requests.post(url, data=data, headers=headers, timeout=15)
            response.raise_for_status()
            samples = response.json().get("data", [])

            if not samples:
                break  # No more data, break the loop

            all_samples.extend(samples)
            page += 1
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            break
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            break
        except requests.exceptions.RequestException as err:
            print(f"Request Exception: {err}")
            break

    return all_samples[:total_entries]  # Ensure we return exactly total_entries

def main():
    api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Replace with your actual API key

    apt28_samples = fetch_all_apt28_samples(api_key, total_entries=1000)

    if apt28_samples:
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(apt28_samples)

        # Convert 'first_seen' and 'last_seen' to datetime
        df['first_seen'] = pd.to_datetime(df['first_seen'])
        df['last_seen'] = pd.to_datetime(df['last_seen'])

        # Count malware samples per day based on 'first_seen'
        timeline_data = df.groupby(df['first_seen'].dt.date).size()

        # Plotting the timeline data
        plt.figure(figsize=(12, 8))
        plt.plot(timeline_data.index, timeline_data.values, marker='o', linestyle='-', color='b', label='APT28 Samples')
        plt.title('APT28 Malware Timeline', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Number of Samples', fontsize=14)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('apt28_timeline.png')

        # Bar chart for file_type counts
        plt.figure(figsize=(10, 6))
        file_type_counts = df['file_type'].value_counts()
        file_type_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Count of Different File Types', fontsize=16, fontweight='bold')
        plt.xlabel('File Type', fontsize=14)
        plt.ylabel('Number of Samples', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('apt28_file_type_counts.png')

        # Save the DataFrame to an Excel file
        excel_file = "apt28_samples.xlsx"
        df.to_excel(excel_file, index=False)

        print(f"Data exported to {excel_file}, timeline plot saved as 'apt28_timeline.png', and file type plot saved as 'apt28_file_type_counts.png'")
    else:
        print("No samples found.")

if __name__ == "__main__":
    main()

