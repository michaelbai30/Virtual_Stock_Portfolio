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

window.onload = loadPortfolio;