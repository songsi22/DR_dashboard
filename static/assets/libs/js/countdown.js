Date.prototype.format = function(f) {
    if (!this.valueOf()) return " ";

    var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
    var d = this;

    return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
        switch ($1) {
            case "yyyy": return d.getFullYear();
            case "yy": return (d.getFullYear() % 1000).zf(2);
            case "MM": return (d.getMonth() + 1).zf(2);
            case "dd": return d.getDate().zf(2);
            case "E": return weekName[d.getDay()];
            case "HH": return d.getHours().zf(2);
            case "hh": return ((h = d.getHours() % 12) ? h : 12).zf(2);
            case "mm": return d.getMinutes().zf(2);
            case "ss": return d.getSeconds().zf(2);
            case "a/p": return d.getHours() < 12 ? "AM" : "PM";
            default: return $1;
        }
    });
};

String.prototype.string = function(len){var s = '', i = 0; while (i++ < len) { s += this; } return s;};
String.prototype.zf = function(len){return "0".string(len - this.length) + this;};
Number.prototype.zf = function(len){return this.toString().zf(len);};

const countDownTimer = function (id, date) {
    var _vDate = new Date(date);
    // 전달 받은 일자
    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distDt = _vDate - now;
        if (distDt < 0) {
            clearInterval(timer);
            document.getElementById(id).textContent = 'RTO 시간 종료';
            return;
        }
        var days = Math.floor(distDt / _day);
        var hours = Math.floor((distDt % _day) / _hour);
        var minutes = Math.floor((distDt % _hour) / _minute);
        var seconds = Math.floor((distDt % _minute) / _second);
        // document.getElementById(id).textContent = date.toLocaleString() + "까지 : ";
        // document.getElementById(id).textContent = days + '일 ';
        document.getElementById(id).textContent = '';
        document.getElementById(id).textContent += hours + '시간 ';
        document.getElementById(id).textContent += minutes + '분 ';
        document.getElementById(id).textContent += seconds + '초';
    }

    timer = setInterval(showRemaining, 1000);
}



// var dateObj = new Date();
// dateObj.setDate(dateObj.getDate() + 1);
var dateObj = new Date();
dateObj.setHours(dateObj.getHours()+12)

// countDownTimer('sample01', dateObj);
// countDownTimer('sample02', '04/01/2024 00:00 AM');
// countDownTimer('sample03', '04/01/2024');
// countDownTimer('sample04', '04/01/2019');
