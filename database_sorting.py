import sqlite3


def sorting_db():
    con = sqlite3.connect('data/data.db')
    cur = con.cursor()

    idNameTask = cur.execute('SELECT * FROM idNameTask').fetchall()
    idNameSubtask = cur.execute('SELECT * FROM idNameSubtask').fetchall()
    idDate = cur.execute('SELECT * FROM idDate').fetchall()
    idTime = cur.execute('SELECT * FROM idTime').fetchall()
    idDatedict = {}
    idTimedict = {}

    for el in idDate:
        edit = el[-1].split('.')
        edit.reverse()
        edit = ''.join(edit)
        if int(edit) not in idDatedict:
            idDatedict[int(edit)] = [el[2], el[0], el[1]]
        else:
            idDatedict[int(edit)].insert(-1, el[1])

    idDate = [idDatedict[key] for key in sorted(idDatedict.keys())]

    for el in idTime:
        edit = el[-1].split(':')
        edit.reverse()
        edit = ''.join(edit)
        if int(edit) not in idTimedict:
            idTimedict[int(edit)] = [el[2], el[0], el[1]]
        else:
            idTimedict[int(edit)].insert(-1, el[1])

    idTime = [idTimedict[key] for key in sorted(idTimedict.keys())]
    idNameTask = cycle_idNameTask_idNameSubtask(idNameTask, idDate, idTime)
    idNameSubtask = cycle_idNameTask_idNameSubtask(idNameSubtask, idDate, idTime)

    if idNameTask != None:
        cur.execute('DELETE FROM idNameTask')
        for el in idNameTask:
            cur.execute('INSERT INTO idNameTask(type, id, name) VALUES("{}", {}, "{}")'.format(el[0], el[1], el[2]))
    if idNameSubtask != None:
        cur.execute('DELETE FROM idNameSubtask')
        for el in idNameSubtask:
            cur.execute('INSERT INTO idNameSubtask(type, id, idTask, name) VALUES("{}", {}, {}, "{}")'.
                        format(el[0], el[1], el[2], el[3]))

    con.commit()


def cycle_idNameTask_idNameSubtask(task_or_subtask, idDate, idTime):
    dict_elements = {}
    for el in task_or_subtask:
        type = el[0]
        id = el[1]
        ind_date = None
        ind_time = None

        for el_date in idDate:
            for i in range(2, len(el_date)):
                if el_date[1] == type and el_date[i] == id:
                    ind_date = idDate.index(el_date)

        for el_time in idTime:
            for i in range(2, len(el_time)):
                if el_time[1] == type and el_time[i] == id:
                    ind_time = idTime.index(el_time)

        if ind_date != None:
            if ind_time == None:
                ind_time = 0
        else:
            ind_date = -1
            ind_time = 0

        if int(str(ind_date) + str(ind_time)) not in dict_elements:
            dict_elements[int(str(ind_date) + str(ind_time))] = [el]
        else:
            dict_elements[int(str(ind_date) + str(ind_time))].append(el)

        task_or_subtask = []

    for el in sorted(dict_elements.keys()):
        task_or_subtask.extend(dict_elements[el])

    return task_or_subtask


sorting_db()
