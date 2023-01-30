import requests
import time
from bs4 import BeautifulSoup
import smtplib
import tkinter as tk
import tkinter.messagebox as tkm

class Processor():
    def __init__(self, p, d, m, age):
        self.p = p
        self.d = d
        self.m = m
        self.age = age
        self.stop = 0
        self.tracker()

    def tracker(self):
        flag = 0
        for t in range(6):
            URL = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={self.p}&date={self.d}"
            headers = {"User Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            data = str(soup)

            final_data = self.str_to_list(data)

            if self.is_available(final_data):
                flag = 1
                break
            if self.stop == 1:
                break

            time.sleep(10)

        if flag == 0 and self.stop == 0:
            tkm.showinfo("showinfo", "No Vaccines Available")


    def is_available(self, final_data):
        if len(final_data) == 0:
            print(tkm.showinfo("showinfo", "No Vaccines Available"))
            self.stop = 1
        else:
            check = "available_capacity"
            flag = 0
            maxcap = -1
            tempdct = {}
            for fd in final_data:
                age_lim = int(fd["min_age_limit"])
                if (age_lim == 18):
                    age_lim = 0
                else:
                    age_lim = 1

                if int(fd[check]) > maxcap and age_lim == self.age:
                    maxcap = int(fd[check])
                    tempdct = fd

            if len(tempdct) == 0:
                print(tkm.showinfo("showinfo", "No Vaccines Available"))
            elif int(tempdct[check]) > 0:
                self.send_mail(tempdct)
                return True
        return False


    def str_to_list(self, data):
        temp = ""
        org_data = []
        for i in range(13, len(data) - 1):
            if data[i] == '{' or data[i] == ',':
                continue
            elif data[i] == '}':
                org_data.append(temp)
                temp = ""
            else:
                temp += data[i]

        final_data = []

        for d in org_data:
            dct = {}
            p = ''
            cnt = 0
            t1 = ""
            t2 = ""
            for c in d:
                if c == '"' and cnt == 1 and p != ':':
                    t1 = t1.replace('"', '')
                    t2 = t2.replace('"', '')
                    dct[t1] = t2
                    t1 = ""
                    t2 = ""
                    cnt = 0

                if c == ':' and cnt == 0:
                    cnt = cnt + 1
                    p = c
                    continue

                if cnt == 0:
                    t1 += c
                else:
                    t2 += c

                p = c

            final_data.append(dct)

        return final_data


    def send_mail(self, arg):
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login("vaxtracker2021@gmail.com", "tracker2021vaccine")
        subject = "Vaccination slot is available"
        b1 = "Hospital: " + arg["name"] + ", " + arg["address"] + "\n" + "Pin Code: " + arg["pincode"] + "\n"
        b2 = "Minimum age limit: " + arg["min_age_limit"] + "\n"
        b3 = "Vaccine: " + arg["vaccine"] + "\n"
        b4 = "No. of doses: " + arg['available_capacity'] + "\n"
        b5 = "Dose 1: " + arg['available_capacity_dose1'] + "\n"
        b6 = "Dose 2: " + arg['available_capacity_dose2'] + "\n"
        b7 = "Fee: " + arg["fee"] + "\n"
        b8= "Book appointment here: https://selfregistration.cowin.gov.in/"+"\n"
        body = b1 + b2 + b3 + b4 + b5 + b6 + b7+b8
        message = f"subject: {subject}\n\n {body}"
        server.sendmail("vaxtracker2021@gmail.com", self.m, message)
        server.quit()
        print("Your mail has been sent successfully")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_layout()

    def create_layout(self):
        label_pin = tk.Label(self)
        label_pin["text"] = "PinCode"
        label_pin["font"] = "Calibri 15"
        label_pin["height"] = 2
        label_pin.grid(row=0, column=0)

        label_date = tk.Label(self)
        label_date["text"] = "Date"
        label_date["font"] = "Calibri 15"
        label_date["height"] = 1
        label_date.grid(row=1, column=0)

        label_mail = tk.Label(self)
        label_mail["text"] = "UserEmail"
        label_mail["font"] = "Calibri 15"
        label_mail["height"] = 2
        label_mail["width"] = 10
        label_mail.grid(row=2, column=0)

        label_age = tk.Label(self)
        label_age["text"] = "AgeLimit"
        label_age["font"] = "Calibri 15"
        label_age["height"] = 1
        label_age.grid(row=3, column=0)

        self.entry_pin = tk.Entry(self)
        self.entry_pin["font"] = "Calibri 15"
        self.entry_pin["width"] = 20
        self.entry_pin.grid(row=0, column=1, columnspan=2)

        self.entry_date = tk.Entry(self)
        self.entry_date["font"] = "Calibri 15"
        self.entry_date["width"] = 20
        self.entry_date.grid(row=1, column=1, columnspan=2)

        self.entry_mail = tk.Entry(self)
        self.entry_mail["font"] = "Calibri 15"
        self.entry_mail["width"] = 20
        self.entry_mail.grid(row=2, column=1, columnspan=2)

        self.val = tk.IntVar()
        rb18 = tk.Radiobutton(self)
        rb18["text"] = "18-44"
        rb18["value"] = 0
        rb18["variable"] = self.val
        rb18["font"] = "Calibri 11"
        rb18.grid(row=3, column=1)

        rb45 = tk.Radiobutton(self)
        rb45["text"] = "45+"
        rb45["value"] = 1
        rb45["variable"] = self.val
        rb45["font"] = "Calibri 11"
        rb45.grid(row=3, column=2)

        btn_sub = tk.Button(self)
        btn_sub["text"] = "SUBMIT"
        btn_sub["font"] = "Calibri 9 bold"
        btn_sub["command"] = self.on_click_sub
        btn_sub.grid(row=4, column=1)

    def on_click_sub(self):
        pin = str(self.entry_pin.get())
        date = str(self.entry_date.get())
        mail = str(self.entry_mail.get())
        age = self.val.get()

        if pin == "" or date == "" or mail == "":
            print(tkm.showerror("showerror", "Enter Valid Data"))
        else:
            self.pro = Processor(pin, date, mail, age)

root = tk.Tk()
root.geometry("350x200")
root.title("Vaccine Tracker")
app = Application(master = root)
app.mainloop()