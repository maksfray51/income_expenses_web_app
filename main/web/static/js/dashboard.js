// функция для конвертации в красивое число
function numberWithSpaces(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

const windowInnerWidth = document.documentElement.clientWidth
const windowInnerHeight = document.documentElement.clientHeight

// data for expenses
var expenses = document.querySelector('.expenses');

var expenses_sums = [];
var expenses_categories = [];

for(const expense of expenses.children) {
  expenses_categories.push(expense.dataset.category);
  expenses_sums.push(expense.dataset.sum);
}

// data for incomes
let incomes = document.querySelector('.incomes');

var incomes_sums = [];
var incomes_categories = []; 

for (const income of incomes.children) {
  incomes_categories.push(income.dataset.category);
  incomes_sums.push(income.dataset.sum); 
};

// data for expenses_to_dates
var expenses_to_dates = document.querySelector('.expenses-to-dates');

var expenses_to_dates_sums = [];
var expenses_to_dates_months = [];

for(const expense_to_date of expenses_to_dates.children) {
  expenses_to_dates_months.push(expense_to_date.dataset.month);
  expenses_to_dates_sums.push(expense_to_date.dataset.sum);
}

// data for incomes_to_dates
var incomes_to_dates = document.querySelector('.incomes-to-dates');

var incomes_to_dates_sums = [];
var incomes_to_dates_months = [];

for(const income_to_dates of incomes_to_dates.children) {
  incomes_to_dates_months.push(income_to_dates.dataset.month);
  incomes_to_dates_sums.push(income_to_dates.dataset.sum);
}



let expenses_ctx = document.querySelector('#expenses-container').getContext('2d');
expenses_ctx.canvas.parentNode.style.height = windowInnerHeight*0.5 + 'px';
expenses_ctx.canvas.parentNode.style.width = windowInnerWidth*0.5 + 'px';

var expense_gradient = expenses_ctx.createLinearGradient(0, 0, 0, 400);
expense_gradient.addColorStop(0, 'rgba(51, 204, 255, 1)');   
expense_gradient.addColorStop(1, 'rgba(255, 153, 204, 1)');


let expenses_chart = new Chart(expenses_ctx, {
    type: 'doughnut',
    data: {
      labels: expenses_categories,
      datasets: [{
          label: 'Категории трат',
          data: expenses_sums,
          backgroundColor: expense_gradient,
          borderJoinStyle: 'bevel',
          hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'smth'
        }
      }
    }
});

let incomes_ctx = document.querySelector('#incomes-container').getContext('2d');
incomes_ctx.canvas.parentNode.style.height = windowInnerHeight*0.5 + 'px';
incomes_ctx.canvas.parentNode.style.width = windowInnerWidth*0.5 + 'px';

var income_gradient = incomes_ctx.createLinearGradient(0, 0, 0, 400);
income_gradient.addColorStop(0, 'rgba(51, 204, 255, 1)');   
income_gradient.addColorStop(1, 'rgba(255, 153, 204, 1)');

let incomes_chart = new Chart(incomes_ctx, {
    type: 'doughnut',
    data: {
      labels: incomes_categories,
      datasets: [{
          label: 'Категории доходов',
          data: incomes_sums,
          backgroundColor: income_gradient,
          borderJoinStyle: 'bevel',
          hoverOffset: 4
      }]
    },
    options: {
      responsive: true
    }
});


let expenses_to_date_ctx = document.querySelector('#expenses-to-dates-container').getContext('2d');

var expenses_to_date_gradient = expenses_to_date_ctx.createLinearGradient(0, 0, 0, 400);
expenses_to_date_gradient.addColorStop(0, 'rgba(51, 204, 255, 1)');   
expenses_to_date_gradient.addColorStop(1, 'rgba(255, 153, 204, 1)');

let expenses_to_date_chart = new Chart(expenses_to_date_ctx, {
  type: 'bar',
  data: {
    labels: expenses_to_dates_months,
    datasets: [
      {
        label: 'Расходы по месяцам',
        data: expenses_to_dates_sums,
        backgroundColor: expenses_to_date_gradient
      }
    ]
  },
  options: {
    responsive: true
  }
});

let incomes_to_date_ctx = document.querySelector('#incomes-to-dates-container').getContext('2d');

var incomes_to_date_gradient = incomes_to_date_ctx.createLinearGradient(0, 0, 0, 400);
incomes_to_date_gradient.addColorStop(0, 'rgba(255, 153, 204, 1)');
incomes_to_date_gradient.addColorStop(1, 'rgba(51, 204, 255, 1)');   


let incomes_to_date_chart = new Chart(incomes_to_date_ctx, {
  type: 'bar',
  data: {
    labels: incomes_to_dates_months,
    datasets: [
      {
        label: 'Доходы по месяцам',
        data: incomes_to_dates_sums,
        backgroundColor: incomes_to_date_gradient
      }
    ]
  },
  options: {
    responsive: true
  }
});