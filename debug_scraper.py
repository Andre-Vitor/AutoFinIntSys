import yfinance as yf
import pandas as pd

def test_scraper(tickers):
    all_news = []
    for ticker in tickers:
        print(f"--- Fetching {ticker} ---")
        tkr = yf.Ticker(ticker)
        news = tkr.news
        
        for item in news:
            content = item.get('content', {}) # Enter the 'content' nest
            all_news.append({
                "ticker": ticker,
                "title": content.get('title'),
                "summary": content.get('summary'), # The LLM will love this
                "publisher": content.get('provider', {}).get('displayName'),
                "date": content.get('pubDate')
            })
    
    df = pd.DataFrame(all_news)
    print("\n✅ SUCCESS! Data Found:")
    print(df[['ticker', 'title', 'publisher']].head()) 
    # Check if summary has text
    print(f"\nSample Summary: {df['summary'].iloc[0][:100]}...") 
    df.to_csv("test_output.csv", index=False)

test_scraper(['NVDA'])