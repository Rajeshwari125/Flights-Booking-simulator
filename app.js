const flights=[{id:1,airline:'IndiGo',time:'10AM',price:4500}];
function searchFlights(){localStorage.setItem('flights',JSON.stringify(flights));location.href='results.html';}
if(document.getElementById('results')){
JSON.parse(localStorage.getItem('flights')).forEach(f=>{
let d=document.createElement('div');d.className='card';
d.innerHTML=`<h3>${f.airline}</h3><p>₹${f.price}</p><button onclick="bookFlight(${f.id})">Book</button>`;
results.appendChild(d);});
}
function bookFlight(id){localStorage.setItem('selectedFlight',JSON.stringify(flights[0]));location.href='booking.html';}
function confirmBooking(){localStorage.setItem('pnr','PNR'+Math.floor(Math.random()*10000));location.href='confirmation.html';}
if(document.getElementById('summary')){summary.innerHTML='PNR: '+localStorage.getItem('pnr');}
function downloadReceipt(){const b=new Blob([localStorage.getItem('pnr')]);const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='receipt.txt';a.click();}