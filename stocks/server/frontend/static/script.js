// listens for user actions and calls flask API app.py via fetch

// fetch latest portfolio data from backend and renders cash balance, total portfolio value, current holdings, and recent transactions
async function loadPortfolio() {
  // call flask api to get full portfolio as json
  const res = await fetch("http://127.0.0.1:5000/api/portfolio");
  const data = await res.json();

  // get asset values
  document.getElementById("cash").textContent = `$${data.cash_balance.toFixed(2)}`;
  document.getElementById("value").textContent = `$${data.portfolio_value.toFixed(2)}`;

  // get holdings
  const holdingsList = document.getElementById("holdings");
  holdingsList.innerHTML = "";

  // check if holdings
  if (Object.keys(data.holdings).length === 0) {
    holdingsList.innerHTML = "<li>No holdings.</li>";
  } 
  else {
    // ex: {"AAPL" : [shares, avg_price], ...}
    for (const [ticker, [shares, avg_price]] of Object.entries(data.holdings)) {
      const li = document.createElement("li");
      li.textContent = `${ticker}: ${shares} shares @ $${avg_price}`;
      holdingsList.appendChild(li);
    }
  }

  // transactions list
  const txList = document.getElementById("transactions");
  txList.innerHTML = "";

  // check if transactions
  if (data.transactions.length === 0) {
    txList.innerHTML = "<li>No transactions yet.</li>";
  } 
  else {
    // show most recent first
    for (const tx of data.transactions.slice().reverse()) {
      const li = document.createElement("li");
      li.textContent = `${tx.time} - ${tx.type} ${tx.shares} ${tx.ticker} @ $${tx.price}`;
      txList.appendChild(li);
    }
  }

  // limit orders list
  const limitList = document.getElementById("limit-orders");
  limitList.innerHTML = "";

  if (data.limit_orders.length == 0){
    limitList.innerHTML = "<li> No limit orders yet. <li>";
  }
  else{
    for (const lo of data.limit_orders.slice().reverse()){
      const li = document.createElement("li");
      li.textContent = `${lo.time} - ${lo.shares} ${lo.ticker} (${lo.type}) @ $${lo.price}`;
      limitList.appendChild(li);
    }
  }

  document.getElementById("stock-info-cash").textContent = `$${data.cash_balance.tofixed(2)}`;
}

// fetch portfolio summary data from backend and render summary table into summary-data
async function loadSummary(){

  // get computed summary (value, cash, allocations)
  const res = await fetch('/api/summary');
  const data = await res.json();

  const summaryText = document.getElementById('summary-data')

  // PL and Allocations Table construction
  // Total portfolio value
  // Cash / buying power
  // Table of each holding
  summaryText.innerHTML=`
    <p><strong> Total Value: </strong> $${data.total_value} </p>
     <p><strong> Buying Power: </strong> $${data.cash_balance} </p>
     <table>
        <thead>
          <tr>
            <th> Ticker </th>
            <th> Shares </th>
            <th> Value </th>
            <th> Allocation% </th>
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

// submit market order to buy to the backend and refreshes the portfolio view
async function buyStock() {

  // read user inputs
  const symbol = document.getElementById("trade-symbol").value.toUpperCase();
  const shares = parseInt(document.getElementById("trade-shares").value);

  // validate inputs
  if (!symbol || !shares || shares <= 0) {
    alert("Invalid Entry: Enter valid symbol and share count");
    return;
  }

  // send POST request to flask api with JSON {symbol, shares}
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

// submit market order to sell to the backend and refreshes the portfolio view
async function sellStock() {

  // read user inputs
  const symbol = document.getElementById("trade-symbol").value.toUpperCase();
  const shares = parseInt(document.getElementById("trade-shares").value);

  // validate inputs
  if (!symbol || !shares || shares <= 0) {
    alert("Invalid Entry: Enter valid symbol and share count");
    return;
  }
  
  // send POST request to flask api
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

// send request to generate chart to api
async function loadChart(period){
  const symbol = document.getElementById('chart-symbol').value.toUpperCase();

  if (!symbol){
    alert("Please enter a ticker symbol.");
    return;
  }
  try{
    // request api to generate chart for symbol, period
    // expected return: {image_path: "/static/chart.html"}
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

// ask api for live price
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

    result.style.color = data.change_percent >= 0 ? "lightgreen" : "red";
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
        'Content-Type': 'application/json' 
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

// function to send request to /api/deposit to deposit funds
async function depositFunds(){
  const input = document.getElementById('deposit-amount')
  const message = document.getElementById('deposit-message')
  const amount = parseFloat(input.value)

  try{
    const result = await fetch('/api/deposit',{
      method: 'POST',
       headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({amount})
    })

    const data = await result.json();

    if (data.error){
      message.style.color = 'red';
      message.textContent = data.error;
      return;
    }

    message.style.color = 'lightgreen';
    message.textContent = data.message;
    input.value='';

  }
  catch(err){
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