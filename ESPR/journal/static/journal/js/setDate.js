var objToday = new Date(),
	weekday = new Array('Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'),
	dayOfWeek = weekday[objToday.getDay()],
	dayOfMonth = objToday.getDate(),
	months = new Array('Janvier', 'Février', 'Mars', 'Avril', 'mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Decembre'),
	curMonth = months[objToday.getMonth()];

var today = dayOfWeek + " " + dayOfMonth + " " + curMonth;

document.getElementById("currentDate").innerHTML = today;