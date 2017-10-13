import psycopg2


db = psycopg2.connect("dbname='lazysql' user='postgres' host='localhost' password='qwe'")


def wrapstr(x):
    """ return 'str' if object is str"""
    if isinstance(x, str):
        return "'" + x + "'"
    else:
        return str(x)

class Base(object):
    def __init__(self):
        # setting __primary_key__
        for k in self.__class__.__dict__.keys():
            if isinstance(self.__class__.__dict__[k], tuple) and\
                    ('PRIMARY KEY' in self.__class__.__dict__[k] or\
                        'primary key' in self.__class__.__dict__[k]):
                self.__dict__['__primary_key__'] = k
        if '__primary_key__' not in self.__dict__.keys():
            raise ValueError('no primary key (you should define "primary key" or "PRIMARY KEY" in class definition')

    def create(self, **kwargs):
        # checking columns
        for k in kwargs:
            if k not in self.__class__.__dict__.keys():
                raise ValueError('Unexpected column name: ' + k)
            self.__dict__[k] = kwargs[k]
        # setting cols and values
        cols, values = self.__cv__(self.__dict__)
        ex = "INSERT INTO {0}\n({1})\nVALUES\n({2});".format(self.__tablename__, cols, values)
        # print(ex)
        arg = dict()
        arg[self.__dict__['__primary_key__']] = self.__dict__[self.__dict__['__primary_key__']]
        result = self.select(**arg)
        if result:
            print('OBJECT ALREADY EXISTS', result)
        else:
            cursor = db.cursor()
            cursor.execute(ex)
            cursor.close()
            db.commit()

    def __create_exists__(self, **kwargs):
        # checking columns
        for k in kwargs:
            if k not in self.__class__.__dict__.keys():
                raise ValueError('Unexpected column name: ' + k)
            self.__dict__[k] = kwargs[k]
        # setting cols and values
        return self

    def __cv__(self, argdict):
        """arguments wrapper for insert sql command"""
        cols = ''
        values = ''
        for k in argdict.keys():
            if k.startswith('__'):
                continue
            cols += k + ', '
            values += wrapstr(argdict[k]) + ", "
        return cols[:-2], values[:-2]

    def update(self, **kwargs):
        if self.__primary_key__ in kwargs.keys():
            raise ValueError('primary key in update call')
        cols = []
        values = []
        for k in kwargs.keys():
            if k not in self.__dict__.keys():
                raise ValueError('unexpected name of column')
            cols.append(k)
            values.append(wrapstr(kwargs[k]))
        updatestring = ''
        for col, val in zip(cols, values):
            updatestring += col + ' = ' + val + ', '
        updatestring = updatestring[:-2]
        ex = "UPDATE {0} SET {1} WHERE {2} = {3};".format(self.__tablename__, updatestring, self.__primary_key__, self.__dict__[self.__primary_key__])
        # print(ex)
        cursor = db.cursor()
        cursor.execute(ex)
        cursor.close()
        db.commit()

    def select(self, **kwargs):
        cv = []
        for k in kwargs.keys():
            if k not in self.__class__.__dict__.keys():
                raise ValueError('unexpected name of column')
            cv.append(k)
            cv.append(kwargs[k])
        if len(cv) > 2:
            raise ValueError('Too many args')
        field_names = [k for k in self.__class__.__dict__.keys() if not k.startswith('__')]
        argsrting = cv[0] + ' = ' + wrapstr(cv[1])
        ex = "SELECT {0} FROM {1} WHERE {2};".format(', '.join(field_names), self.__tablename__, argsrting)
        # print(ex)
        cursor = db.cursor()
        cursor.execute(ex)
        result = []
        for item in cursor.fetchall():
            result.append({k: v for k, v in zip(field_names, item)})
        cursor.close()
        res = []
        for item in result:
            a = self.__class__()
            a.__create_exists__(**item)
            res.append(a)
        return res

    def selectone(self, **kwargs):
        res = self.select(**kwargs)
        if len(res) > 1:
            raise ValueError('too many object was returned by request')
        if len(res) == 0:
            return None
        return res[0]


def viewtable(obj):
    field_names = [k for k in obj.__dict__.keys() if not k.startswith('__')]
    print(field_names, obj.__tablename__)
    ex = 'SELECT %s FROM %s;' % (', '.join(field_names), obj.__tablename__)
    cursor = db.cursor()
    cursor.execute(ex)
    result = cursor.fetchall()
    cursor.close()
    return result


def gettables():
    cursor = db.cursor()
    cursor.execute("SELECT table_name "
                   "FROM information_schema.tables "
                   "WHERE table_type = 'BASE TABLE' "
                   "AND table_schema NOT IN ('pg_catalog', 'information_schema');")
    tables = [t[0] for t in cursor.fetchall()]
    cursor.close()
    return tables


def exists_table(name):
    if name in gettables():
        return True
    return False


def maketable(clsname):
    cursor = db.cursor()
    for cls in Base.__subclasses__():
        if cls.__name__ == clsname:
            cols = ''
            for key in cls.__dict__.keys():
                if not key.startswith('__'):
                    cols += '{0} {1},\n'.format(key, ' '.join(cls.__dict__[key]))
            ex = """CREATE TABLE {0} (\n{1});""".format(cls.__tablename__, cols[:-2])  # -2 remove last ','
            print('CREATE TABLE {}'.format(cls.__tablename__))
            cursor.execute(ex)
    cursor.close()
    db.commit()


def update_all():
    """checking and updating db tables"""
    tablenames = []
    for cls in Base.__subclasses__():
        tablenames.append(cls.__tablename__)
        if not exists_table(cls.__tablename__):
            maketable(cls.__name__)
    cursor = db.cursor()
    for table in gettables():
        if table not in tablenames:
            print('Do you want delete table "{}"?(y/n) '.format(table), end=" ")
            yn = input()
            if yn == 'y' or yn == 'Y':
                print('DROP TABLE "{}";'.format(table))
                cursor.execute('DROP TABLE "{}";'.format(table))
                db.commit()
    cursor.close()
    print('tablenames ', tablenames)

