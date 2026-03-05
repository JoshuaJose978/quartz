---
title: SearXNG API Documentation and Usage Guide
---


SearXNG is a privacy-respecting metasearch engine that allows you to search across multiple sources. This guide provides comprehensive examples for interacting with SearXNG via its API, with practical examples tailored to specific search engines and categories.

## Basic API Usage

### GET Request Format

```bash
curl -G "https://your-searxng-instance-url/" --data-urlencode "q=your search query" [additional parameters]
```

### POST Request Format (for complex queries)

```bash
curl -X POST "https://your-searxng-instance-url/search" \
  -H "Content-Type: application/json" \
  -d '{ "q": "your search query", [additional parameters as JSON] }'
```

## Core Parameters

|Parameter|Description|Example Value|
|---|---|---|
|q|Search query|"climate change research"|
|categories|Search categories|"general,science"|
|engines|Specific engines to use|"google,duckduckgo,brave"|
|language|Language of results|"en"|
|format|Response format|"json"|
|time_range|Time filter|"day", "week", "month", "year"|
|safesearch|Safe search level|0 (off), 1 (moderate), 2 (strict)|
|page|Result page number|1, 2, 3, etc.|
|enabled_plugins|Enabled plugins|"Tracker_URL_remover,Ahmia_blacklist"|
|disabled_plugins|Disabled plugins|"Vim-like_hotkeys,Tor_check_plugin"|

## Category-Specific Examples

### Web Search Examples

#### 1. Basic Web Search with Popular Engines

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=renewable energy solutions" \
  --data-urlencode "categories=web" \
  --data-urlencode "engines=google,brave,duckduckgo" \
  --data-urlencode "format=json"
```

#### 2. Web Search with Safe Search Enabled

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=educational content" \
  --data-urlencode "categories=web" \
  --data-urlencode "engines=google,startpage" \
  --data-urlencode "safesearch=2" \
  --data-urlencode "format=json"
```

#### 3. Localized Search with Regional Results

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=local restaurants" \
  --data-urlencode "categories=web" \
  --data-urlencode "engines=bing,google" \
  --data-urlencode "language=fr" \
  --data-urlencode "format=json"
```

### Image Search Examples

#### 1. Finding Free-to-Use Images

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=mountain landscape photography" \
  --data-urlencode "categories=images" \
  --data-urlencode "engines=openverse,unsplash,pdia" \
  --data-urlencode "format=json"
```

#### 2. Comprehensive Image Search Across Multiple Engines

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=cyberpunk art" \
  --data-urlencode "categories=images" \
  --data-urlencode "engines=google_images,bing_images,brave.images,qwant_images" \
  --data-urlencode "format=json"
```

#### 3. Stock Image Search for Commercial Use

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=business meeting professionals" \
  --data-urlencode "categories=images" \
  --data-urlencode "engines=adobe_stock,unsplash" \
  --data-urlencode "format=json"
```

### Video Search Examples

#### 1. Search Across Alternative Video Platforms

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=documentary nature" \
  --data-urlencode "categories=videos" \
  --data-urlencode "engines=invidious,piped,peertube,odysee" \
  --data-urlencode "format=json"
```

#### 2. Family-Friendly Video Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=educational animation for kids" \
  --data-urlencode "categories=videos" \
  --data-urlencode "engines=youtube_noapi,bing_videos" \
  --data-urlencode "safesearch=2" \
  --data-urlencode "format=json"
```

#### 3. Recent Video Content with Time Range

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=latest technology reviews" \
  --data-urlencode "categories=videos" \
  --data-urlencode "engines=google_videos,brave.videos" \
  --data-urlencode "time_range=week" \
  --data-urlencode "format=json"
```

### News Search Examples

#### 1. Recent News from Multiple Sources

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=climate policy developments" \
  --data-urlencode "categories=news" \
  --data-urlencode "engines=google_news,bing_news,brave.news,qwant_news" \
  --data-urlencode "format=json"
```

#### 2. Financial News with Time Filter

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=stock market analysis" \
  --data-urlencode "categories=news" \
  --data-urlencode "engines=google_news,yahoo_news,reuters" \
  --data-urlencode "time_range=day" \
  --data-urlencode "format=json"
```

#### 3. News in a Specific Language

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=political developments" \
  --data-urlencode "categories=news" \
  --data-urlencode "engines=qwant_news,bing_news" \
  --data-urlencode "language=de" \
  --data-urlencode "format=json"
```

### Academic & Scientific Search Examples

#### 1. Research Paper Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=quantum computing algorithms" \
  --data-urlencode "categories=science" \
  --data-urlencode "engines=arxiv,semantic_scholar,google_scholar" \
  --data-urlencode "format=json"
```

#### 2. Medical Research Query

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=mRNA vaccine development" \
  --data-urlencode "categories=science" \
  --data-urlencode "engines=pubmed,google_scholar" \
  --data-urlencode "format=json"
```

#### 3. Open Access Dataset Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=climate data collection" \
  --data-urlencode "categories=science" \
  --data-urlencode "engines=openairedatasets,openairepublications" \
  --data-urlencode "format=json"
```

### IT & Development Examples

#### 1. Software Development Q&A Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=python async function best practices" \
  --data-urlencode "categories=it" \
  --data-urlencode "engines=stackoverflow,askubuntu,superuser" \
  --data-urlencode "format=json"
```

#### 2. Code Repository Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=golang http server framework" \
  --data-urlencode "categories=it" \
  --data-urlencode "engines=github,gitlab,codeberg" \
  --data-urlencode "format=json"
```

#### 3. Package Registry Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=authentication middleware" \
  --data-urlencode "categories=it" \
  --data-urlencode "engines=npm,pypi,packagist" \
  --data-urlencode "format=json"
```

## Advanced Use Cases

### 1. Multi-Category Search (Web + News + Scientific)

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=AI ethics regulation" \
  --data-urlencode "categories=web,news,science" \
  --data-urlencode "engines=google,bing_news,google_scholar" \
  --data-urlencode "time_range=year" \
  --data-urlencode "format=json"
```

### 2. Combining Translations with Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=machine learning applications healthcare" \
  --data-urlencode "categories=web,science" \
  --data-urlencode "engines=google,google_scholar" \
  --data-urlencode "language=en" \
  --data-urlencode "enabled_plugins=Tracker_URL_remover" \
  --data-urlencode "format=json"
```

### 3. Map Search for Location Data

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=renewable energy plants europe" \
  --data-urlencode "categories=map" \
  --data-urlencode "engines=openstreetmap,photon" \
  --data-urlencode "format=json"
```

### 4. Music and Audio Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=ambient electronic Creative Commons" \
  --data-urlencode "categories=music" \
  --data-urlencode "engines=soundcloud,bandcamp,wikicommons.audio" \
  --data-urlencode "format=json"
```

### 5. Social Media Search

```bash
curl -G "https://your-searxng-instance-url/" \
  --data-urlencode "q=privacy technology" \
  --data-urlencode "categories=social_media" \
  --data-urlencode "engines=mastodon_hashtags,lemmy_posts" \
  --data-urlencode "format=json"
```

## Troubleshooting

### Common Issues and Solutions

1. **Request Timeout**
    
    - Use fewer engines per request
    - Split complex queries into multiple simpler ones
2. **No Results**
    
    - Try different engine combinations
    - Simplify your search terms
    - Check language settings
3. **Rate Limiting**
    
    - Implement request delays between API calls
    - Reduce query frequency
4. **Handling Response Errors**
    
    - Add error checking to handle HTTP status codes
    - Implement retries with exponential backoff

### Example: Error Handling Script

```bash
#!/bin/bash
# Example script with error handling

QUERY="your search query"
INSTANCE="https://your-searxng-instance-url/"

# Function to handle retries
search_with_retry() {
  local max_retries=3
  local retry_count=0
  local wait_time=2
  
  while [ $retry_count -lt $max_retries ]; do
    response=$(curl -s -o response.json -w "%{http_code}" -G "$INSTANCE" \
      --data-urlencode "q=$QUERY" \
      --data-urlencode "format=json")
      
    if [ "$response" -eq 200 ]; then
      cat response.json
      return 0
    else
      echo "Error: HTTP status $response. Retrying in $wait_time seconds..."
      sleep $wait_time
      retry_count=$((retry_count + 1))
      wait_time=$((wait_time * 2))
    fi
  done
  
  echo "Failed after $max_retries retries."
  return 1
}

# Execute search with retry logic
search_with_retry
```

---

This guide should help you effectively utilize SearXNG's API with a deeper understanding of the available engines and their capabilities. Customize the examples to match your specific search requirements and privacy preferences.
