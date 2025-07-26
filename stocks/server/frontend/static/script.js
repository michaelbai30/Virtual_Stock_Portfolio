async function loadPortfolio() {
  const res = await fetch("http://127.0.0.1:5000/api/portfolio");
  const data = await res.json();

  // get asset values
  document.getElementById("cash").textContent = `$${data.cash_balance.toFixed(2)}`;
  document.getElementById("value").textContent = `$${data.portfolio_value.toFixed(2)}`;

  // get holdings
  const holdingsList = document.getElementById("holdings");
  holdingsList.innerHTML = "";

  if (Object.keys(data.holdings).length === 0) {
    holdingsList.innerHTML = "<li>No holdings.</li>";
  } 
  else {
    for (const [ticker, [shares, avg_price]] of Object.entries(data.holdings)) {
      const li = document.createElement("li");
      li.textContent = `${ticker}: ${shares} shares @ $${avg_price}`;
      holdingsList.appendChild(li);
    }
  }

  // transactions
  const txList = document.getElementById("transactions");
  txList.innerHTML = "";

  if (data.transactions.length === 0) {
    txList.innerHTML = "<li>No transactions yet.</li>";
  } 
  else {
    for (const tx of data.transactions.slice().reverse()) {
      const li = document.createElement("li");
      li.textContent = `${tx.time} - ${tx.type} ${tx.shares} ${tx.ticker} @ $${tx.price}`;
      txList.appendChild(li);
    }
  }
}


async function loadSummary(){
  const res = await fetch('/api/summary');
  const data = await res.json();

  const summaryText = document.getElementById('summary-data')
  // PL and Allocations Table construction
  summaryText.innerHTML=`
    <p><strong> Total Value: </strong> $${data.total_value} </p>
     <p><strong> Buying Power: </strong> $${data.cash_balance} </p>
     <table>
        <thead>
          <tr>
            <th> Ticker </th>
            <th> Shares </th>
            <th> Value </th>
            <th> Allocatio n% </th>
            <th> Profit/Loss </th>
            <th> PL % </th>
          </tr>
        </thead>
        <tbody>
          ${data.allocations.map(asset =>`
            <tr>
              <td>${asset.ticker}</td>
              <td>${asset.shares}</td>
              <td>$${asset.current_value}</td>
              <td>${asset.allocation_percent}%</td>
              <td style="color:${asset.profit_loss >= 0 ? 'green' : 'red'}">$${asset.profit_loss}</td>
              <td style="color:${asset.profit_loss_percent >= 0 ? 'green' : 'red'}">${asset.profit_loss_percent}%</td>
            </tr>
            `).join('')}
        </tbody>
     </table>
  `;
}

async function buyStock() {
  const symbol = document.getElementById("trade-symbol").value.toUpperCase();
  const shares = parseInt(document.getElementById("trade-shares").value);

  if (!symbol || !shares || shares <= 0) {
    alert("Invalid Entry: Enter valid symbol and share count");
    return;
  }

  const res = await fetch("http://127.0.0.1:5000/api/buy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, shares })
  });

  const json = await res.json();
  if (json.error) {
    alert(json.error);
  } 
  else {
    alert(json.message || JSON.stringify(json)); // alert successful purchase
  }
  loadPortfolio();  
}

async function sellStock() {
  const symbol = document.getElementById("trade-symbol").value.toUpperCase();
  const shares = parseInt(document.getElementById("trade-shares").value);

  if (!symbol || !shares || shares <= 0) {
    alert("Invalid Entry: Enter valid symbol and share count");
    return;
  }

  const res = await fetch("http://127.0.0.1:5000/api/sell", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, shares })
  });

  const json = await res.json();
  if (json.error) {
    alert(json.error);
  } 
  else {
    alert(json.message || JSON.stringify(json));
  }
  loadPortfolio();
}

async function loadChart(period){
  const symbol = document.getElementById('chart-symbol').value.toUpperCase();
  if (!symbol){
    alert("Please enter a ticker symbol.");
    return;
  }

  try{
    const res = await fetch(`/api/chart?symbol=${symbol}&period=${period}`);
    const data = await res.json();

    if (data.error) {
      alert(`Error: ${data.error}`);
      return;
    }
  
    const img = document.getElementById('chart-frame');
    img.src = data.image_path + '?t=' + new Date().getTime();
  }
  catch(err){
    alert("Error Loading Chart");
    console.error(err);
  }
}

async function getLivePrice(){
  const ticker = document.getElementById('lookup-ticker').value.trim();
  const result = document.getElementById('live-price-result');

  if (!ticker){
    return;
  }

  try{
      const res = await fetch(`/api/price/${ticker}`);
      const data = await res.json();

      if (data.error){
        result.textContent = "Invalid ticker.";
        return;
      }
      // display ticker, price, change percent, and color based on P/L
      result.innerHTML = `
        <strong>${data.ticker}</strong>: $${data.price} 
        (${data.change_percent > 0 ? '+' : ''}${data.change_percent}%)`;

    result.style.color = data.change_percent >= 0 ? "green" : "red";
  } 
    catch (err) {
      result.textContent = "Error fetching data.";
    }
}

// function to submit limit and stop orders to backend API
async function submitLimitOrder(){

  // get user input values from the form fields
  const ticker = document.getElementById("limit-symbol").value.trim();
  const shares = parseInt(document.getElementById("limit-shares").value);
  const price = parseFloat(document.getElementById("limit-price").value);
  const orderType = document.getElementById("limit-type").value;
  const result = document.getElementById("limit-order-result");

  // validate inputs
  if (!ticker || isNaN(shares) || isNaN(price) || shares <= 0 || price <= 0){
    result.textContent = "Invalid input.";
    result.style.color = "red";
    return;
  }


 try {
    // make a post request to backend with order details
    const res = await fetch('/api/limit-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json' // indicate a json is being sent 
      },
      body: JSON.stringify({
        ticker: ticker,
        shares: shares,
        price: price,
        order_type: orderType // LB, SB, LS or SL
      })
    });

    // parse response from backend (res)
    const data = await res.json();

    if (data.error) {
      result.textContent = data.error;
      result.style.color = "red";
    } else {
      result.textContent = data.message;
      result.style.color = "green";
    }
  } catch (err) {
    result.textContent = "Error submitting order.";
    result.style.color = "red";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadPortfolio();
  loadSummary();

  // load 1y AAPL chart by default
  document.getElementById('chart-symbol').value = 'AAPL';
  loadChart('1y');
  
  // load AAPL live price by defualt
  document.getElementById('lookup-ticker').value = 'AAPL';
  getLivePrice();

  setInterval(() => { // query for live price and portfolio changes every 10 seconds
    loadPortfolio();
    loadSummary();

    const ticker = document.getElementById('lookup-ticker').value.trim();
    if (ticker) {
      getLivePrice();
    }
  }, 10000);
});