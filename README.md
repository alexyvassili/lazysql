Написать ORM и отладить её работу на sqlite. Необходимая функциональность:

    создание/удаление таблиц;
        --реализовано наличием/отсутствием описания соответствующего класса
    insert/update
        --insert реализован методом create()
        --update реализован методом update()
    select с указанием необходимых столбцов;
        --select возвращает список объектов с полями, соответствующими столбцам
        --selectone возвращает один такой объект
    обработка базовых ошибок (нет таблицы, нет столбца, не указано значение у обязательного столбца);
        --обработка ошибок по минимуму
    поддержка foreign key и автоджоин таблиц, на которые есть fk.
        --нет
