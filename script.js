// файл script.js
window.onload = function(){

    let a = ''
    let b = ''
    let expressionResult = ''
    let selectedOperation = null

// окно вывода результата
    outputElement = document.getElementById("result")

// список объектов кнопок циферблата (id которых начинается с btn_digit_)
    digitButtons = document.querySelectorAll('[id ^= "btn_digit_"]')

    const MAX_DIGITS = 15; // Максимальное количество цифр

    function onDigitButtonClicked(digit) {
        if (!selectedOperation) {
            if (a.length < MAX_DIGITS) { // Проверка длины
                if ((digit != '.') || (digit == '.' && !a.includes(digit))) {
                    a += digit;
                }
                outputElement.innerHTML = a;
            }
        } else {
            if (b.length < MAX_DIGITS) { // Проверка длины
                if ((digit != '.') || (digit == '.' && !b.includes(digit))) {
                    b += digit;
                    outputElement.innerHTML = b;
                }
            }
        }
    }
// устанавка колбек-функций на кнопки циферблата по событию нажатия
    digitButtons.forEach(button => {
        button.onclick = function() {
            const digitValue = button.innerHTML
            onDigitButtonClicked(digitValue)
        }
    });

// установка колбек-функций для кнопок операций
    document.getElementById("btn_op_mult").onclick = function() {
        if (a === '') return
        selectedOperation = 'x'
        outputElement.innerHTML = a*b
    }
    document.getElementById("btn_op_plus").onclick = function() {
        if (a === '') return
        selectedOperation = '+'
        outputElement.innerHTML = a+b

    }
    document.getElementById("btn_op_minus").onclick = function() {
        if (a === '') return
        selectedOperation = '-'
    }
    document.getElementById("btn_op_div").onclick = function() {
        if (a === '') return
        selectedOperation = '/'
    }
    document.getElementById("btn_op_percent").onclick = function() {
        if (a === '') return
        selectedOperation = '%'
    }
    document.getElementById("btn_op_sign").onclick = function() {
        if (a !== '') {
            a = (parseFloat(a) * -1).toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("backspace").onclick = function() {
        if (!selectedOperation) {
            a = a.slice(0, -1); // Удаляем последний символ из a
            if (a === '') {
                outputElement.innerHTML = 0; // Если a пустое, показываем 0
            } else {
                outputElement.innerHTML = a; // Обновляем вывод
            }
        } else {
            b = b.slice(0, -1); // Удаляем последний символ из b
            if (b === '') {
                outputElement.innerHTML = a; // Если b пустое, показываем a
            } else {
                outputElement.innerHTML = b; // Обновляем вывод
            }
        }
    }
    document.getElementById("lg").onclick = function() {
        if (a !== '') {
            a = Math.log10(parseFloat(a)).toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("ln").onclick = function() {
        if (a !== '') {
            a = Math.log(parseFloat(a)).toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("three_null").onclick = function() {
        if (a === '' || a === '0') {
            a = '000';
        } else if (a.length + 3 <= MAX_DIGITS) { // Проверка длины
            a += '000';
        } else {
            console.log("Достигнуто максимальное количество цифр.");
        }
        outputElement.innerHTML = a; // Обновляем вывод
    }
    document.getElementById("root").onclick = function() {
        if (a !== ''){
            a = Math.sqrt(parseFloat(a)).toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("square").onclick = function() {
        if (a !== '') {
            a = (parseFloat(a) ** 2).toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("factorial").onclick = function() {
        if (a !== '') {
            let num = parseInt(a);
            let factorial = 1;
            for (let i = 1; i <= num; i++) {
                factorial *= i;
            }
            a = factorial.toString();
            outputElement.innerHTML = a;
        }
    }
    document.getElementById("pi").onclick = function() {
        a = Math.PI.toString();
        outputElement.innerHTML = a;
    }

// кнопка очищения
    document.getElementById("btn_op_clear").onclick = function() {
        a = ''
        b = ''
        selectedOperation = ''
        expressionResult = ''
        outputElement.innerHTML = 0
    }


// кнопка расчёта результата
    document.getElementById("btn_op_equal").onclick = function() {
        if (a === '' || b === '' || !selectedOperation)
            return

        switch(selectedOperation) {
            case 'x':
                expressionResult = (+a) * (+b)
                break;
            case '+':
                expressionResult = (+a) + (+b)
                break;
            case '-':
                expressionResult = (+a) - (+b)
                break;
            case '/':
                expressionResult = (+a) / (+b)
                break;
            case '%':
                expressionResult = (+a) % (+b)
                break;



        }
        if (parseFloat(expressionResult)>1e10) expressionResult = parseFloat(expressionResult).toExponential(4);
        else
        {
            if (Number.isInteger(expressionResult)) expressionResult = expressionResult.toString();
            else expressionResult = parseFloat(expressionResult).toFixed(2);
        }

        a = expressionResult.toString()
        b = ''
        selectedOperation = null

        outputElement.innerHTML = a
    }
};
function toggleMenu() {
    const submenu = document.getElementById('submenu');
    submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
};

// script.js
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("switch_theme").onclick = function() {
        console.log("Кнопка нажата"); // Проверка нажатия кнопки
        document.body.classList.toggle('theme-background--dark');
        console.log("Класс theme-background--dark добавлен:", document.body.classList.contains('theme-background--dark'));
    }
});