const videos = [
    { id: 1, title: "Влог о путешествиях", views: 100, user: "Алексей", duration: 300, likes: 50, dislikes: 5, uploadDate: "2023-01-15" },
    { id: 2, title: "Рецепты на каждый день", views: 200, user: "Мария", duration: 600, likes: 80, dislikes: 2, uploadDate: "2023-02-20" },
    { id: 3, title: "Обзор технологий", views: 150, user: "Алексей", duration: 450, likes: 30, dislikes: 1, uploadDate: "2023-03-10" },
    { id: 4, title: "Фитнес тренировка", views: 300, user: "Светлана", duration: 360, likes: 100, dislikes: 10, uploadDate: "2023-04-05" },
];
// 1.1 Функция для конкатенации строк с разделителем
function concatenate(arr, separator) {
    return arr.join(separator);
}

// 1.3 Функция для подсчета суммы квадратов просмотров
function sumOfSquares(arr) {
    let sum = 0;
    for (let video of arr) {
        sum += video.views ** 2;
    }
    return sum;
}

// 1.8 Функция для вычисления среднего арифметического просмотров
function averageViews(arr) {
    let total = 0;
    for (let video of arr) {
        total += video.views;
    }
    return total / arr.length;
}
// 1.10 Функция для очистки массива от нежелательных значений
function erase(arr) {
    return arr.filter(item =>
        item !== false &&
        item !== undefined &&
        item !== '' &&
        item !== 0 &&
        item !== null
    );
}
// 2.8 Функция для получения суммы уникальных просмотров
function sumOfUniqueViews(arr) {
    const uniqueViews = new Set(arr.map(video => video.views));
    let sum = 0;
    for (let view of uniqueViews) {
        sum += view;
    }
    return sum;
}

// Функция для подсчета общего количества лайков
function totalLikes(arr) {
    let total = 0;
    for (let video of arr) {
        total += video.likes;
    }
    return total;
}

// Функция для подсчета общего количества дизлайков
function totalDislikes(arr) {
    let total = 0;
    for (let video of arr) {
        total += video.dislikes;
    }
    return total;
}

// Функция для получения средней длительности видео
function averageDuration(arr) {
    let totalDuration = 0;
    for (let video of arr) {
        totalDuration += video.duration;
    }
    return totalDuration / arr.length;
}

// 3.1 Функция для объединения объектов
function merge(...objects) {
    const result = {};
    for (const obj of objects) {
        for (const key in obj) {
            if (!result.hasOwnProperty(key)) {
                result[key] = obj[key];
            }
        }
    }
    return result;
}
function arr_func(arr) {
    if (arr.length === 0) return [];
    let result = [arr[arr.length - 1]];
    for (let i = arr.length - 1; i >= 0; i--)
    {
        result = [arr[i], result];
    }

    return result;
}

const a = [3, 4, 5, 6, 7];
let b=arr_func(a);
console.log(b);

//
//
// console.log("1.1 Конкатенация:", concatenate(['Я','Учусь','на','лучшей','кафедре'], ' '));
// console.log("1.10 Очистка массива:", erase([0, 1, false, 2, undefined, '', 3, null]));
//
// // Пример использования функций
// console.log("Сумма квадратов просмотров:", sumOfSquares(videos));
// console.log("Среднее количество просмотров:", averageViews(videos));
// console.log("Сумма уникальных просмотров:", sumOfUniqueViews(videos));
// console.log("Общее количество лайков:", totalLikes(videos));
// console.log("Общее количество дизлайков:", totalDislikes(videos));
// console.log("Средняя длительность видео (в секундах):", averageDuration(videos));
//
// // Объединение информации о видео
// const additionalVideos = [
//     { id: 5, title: "Как научиться программировать", views: 400, user: "Светлана", duration: 720, likes: 200, dislikes: 3, uploadDate: "2023-05-01" },
//     { id: 6, title: "Обзор новых гаджетов", views: 150, user: "Мария", duration: 540, likes: 60, dislikes: 4, uploadDate: "2023-06-10" },
// ];
//
// const mergedVideos = merge(...videos, ...additionalVideos);
// console.log("Объединенные видео:", mergedVideos);
//
//
// const obj1 = { a: 1, b: 2 };
// const obj2 = { b: 3, c: 4 };
// const obj3 = { d: 5 };
//
// const mergedObject = merge(obj1, obj2, obj3);
// console.log(mergedObject); // { a: 1, b: 2, c: 4, d: 5 }
//
//
// const video1 = { title: "Влог о путешествиях", views: 100, likes: 50, dislikes: 5, uploadDate: "2023-01-15" };
// const video2 = { title: "Рецепты на каждый день", views: 200, likes: 80, dislikes: 2, uploadDate: "2023-02-20" };
// const video3 = { title: "Обзор технологий", views: 150, likes: 30, dislikes: 1, uploadDate: "2023-03-10" };
//
// const mergedVideo = merge(video1, video2, video3);
// console.log(mergedVideo);