import logging
import time
from kiteconnect import KiteConnect
import matplotlib.pyplot as plt
from datetime import datetime

# --- API Credentials and Setup ---
# Replace with your actual API key and secret
api_key = "<YOUR_API_KEY>"
api_secret = "<YOUR_API_SECRET>"

# Replace with the request token you obtain from the login URL
request_token = "YOUR_REQUEST_TOKEN"

myshares = ["BANDHANBNK", "BHARATFORG", "CHAMBLFERT", "GODREJAGRO", "GRAPHITE", "HCC", "HCL-INSYS", "HEG", "ITC", "LICI", "LT", "MOTHERSON", "NTPC", "OLAELEC", "PRAJIND", "RBLBANK", "RELIANCE", "RENUKA", "RPOWER", "SAMMAANCAP", "SOUTHBANK", "SRF", "STLNETWORK", "STLTECH", "SUBEXLTD", "SYRMA", "TATATECH", "TEJASNET","VAKRANGEE", "YESBANK"]

# Initialise KiteConnect
kite = KiteConnect(api_key=api_key)

# Get a login URL
# When you first run this, visit the URL, log in, and copy the request token from the redirect URL
def get_login_url():
    print(kite.login_url())

# If you need to generate a new access token, uncomment the line below and run the script
# get_login_url()

# Generate and set the access token
try:
    #data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(request_token)
except Exception as e:
    logging.error(f"Failed to generate session or set access token: {e}")
    exit()

# --- Aggregate P&L from Holdings ---
def aggregate_holdings_pnl():
    """
    Fetches Zerodha holdings via Kite API and calculates the aggregated day's P&L.
    """
    try:
        holdings_response = kite.holdings()
        
        print("Fetched holdings successfully.",holdings_response)
        total_day_pnl = 0
        
        # Loop through each holding and sum the daily change
        for holding in holdings_response:
            if holding["tradingsymbol"] in myshares:
                total_day_pnl += holding["day_change"] * holding["quantity"]
                #print(f"Holding: {holding['tradingsymbol']}, Day change is : {holding['day_change']} Holding qty is: {holding['quantity']:.2f}")
            
        return total_day_pnl
        
    except Exception as e:
        logging.error(f"Failed to fetch holdings or calculate P&L: {e}")
        return None

def start_live_pnl_tracking():
    """
    Starts live tracking of P&L and plots it.
    """
    pnl_values = []
    timestamps = []
    
    plt.ion()
    fig, ax = plt.subplots()
    
    while True:
        current_pnl = aggregate_holdings_pnl()
        if current_pnl is not None:
            pnl_values.append(current_pnl)
            timestamps.append(datetime.now())
            
            ax.clear()
            ax.plot(timestamps, pnl_values, marker='o')
            ax.set_title("Live P&L Tracking")
            ax.set_xlabel("Time")
            ax.set_ylabel("P&L")
            plt.draw()
            plt.pause(10)  # Update every 60 seconds

def start_live_pnl_tracking_2():
    """
    Continuously fetch and log live P&L every `interval` seconds.
    Plots it as a wave (oscillating around zero baseline) like an intraday Nifty chart.
    """
    global pnl_log
    plt.ion()  # Interactive plotting

    base_pnl = None  # reference baseline to plot relative change

    while True:
        pnl = aggregate_holdings_pnl()

        time.sleep(10)  # Fetch P&L every 10 seconds
        if False:
        #if pnl is not None:
            timestamp = datetime.now()

            # Set baseline on first reading
            if base_pnl is None:
                base_pnl = pnl

            # Relative P&L (oscillates around zero)
            rel_pnl = pnl - base_pnl

            # Append to log
            #pnl_log.loc[len(pnl_log)] = [timestamp, rel_pnl]
            #pnl_log.to_csv(log_file, index=False)

            # --- Live Plot ---
            plt.clf()
            plt.plot(
                timestamp,
                pnl,
                color="dodgerblue",
                linewidth=2,
                label="Live Relative P&L"
            )
            plt.axhline(0, color="gray", linestyle="--", linewidth=1)  # Zero baseline
            plt.title("Live Intraday P&L (Zero Baseline View)")
            plt.xlabel("Time")
            plt.ylabel("P&L Change (₹)")
            plt.legend(loc="upper left")
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.pause(10)

            print(f"[{timestamp.strftime('%H:%M:%S')}] ΔP&L: {rel_pnl:+.2f}  (Total P&L: {pnl:.2f})")

# --- Main execution ---
if __name__ == "__main__":
    #total_pnl = aggregate_holdings_pnl()
    start_live_pnl_tracking_2()
    #if total_pnl is not None:
        #print(f"Aggregated day's P&L for all holdings: {total_pnl:.2f}")

