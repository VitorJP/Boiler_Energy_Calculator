import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from pyfluids import Fluid, FluidsList, Input

Table_Fuels = [['Hydrogen', 119.96, 141.88, ''],
               ['Natural gas', 47.13, 52.21, ''],
               ['Crude oil', 42.68, 45.53, ''],
               ['Coal', 22.73, 23.96, ''],
               ['Cocking coal', 28.60, 29.86, ''],
               ['Farmed trees', 19.55, 20.58, ''],
               ['Herbaceous biomass', 17.21, 18.12, ''],
               ['Corn stover', 16.37, 17.41, ''],
               ['Forest residue', 15.40, 16.47, ''],
               ['Sugarcane bagasse', 16.7, 18.03, '']]
# Fuel name, Lower Heating Value (MJ/kg), Higher Heating Value (MJ/kg), hydrogen content


def input_int(msg):
    while True:
        try:
            return int(input(msg))
        except TypeError:
            print('Not a valid number!')


def input_float(msg):
    f = -1
    while True:
        try:
            f = float(input(msg))
        except TypeError:
            print('Not a valid number!')

        if f >= 0:
            return f
        else:
            print('Not a valid number (number cannot be negative)!')


def input_limited_float(msg, bottom, top, only_less, only_more):
    limited_float = input_float(msg)
    if only_less:
        bottom_limit = (limited_float < bottom)
    else:
        bottom_limit = (limited_float <= bottom)

    if only_more:
        top_limit = (limited_float > top)
    else:
        top_limit = (limited_float >= top)

    while bottom_limit or top_limit:
        print(f'Not a valid number (the number must be between {bottom} and {top})')
        limited_float = input_float(msg)
        if only_less:
            bottom_limit = (limited_float < bottom)
        else:
            bottom_limit = (limited_float <= bottom)

        if only_more:
            top_limit = (limited_float > top)
        else:
            top_limit = (limited_float >= top)

    return limited_float


def show_list_fuels(complete, row=0):
    def show_header():
        name, lhv, hhv, hc = 'Fuel:', 'LHV (MJ/kg):', 'HHV (MJ/kg):', 'Hydrogen %:'
        print(f'\n{name:<32} {lhv:>16} {hhv:>16} {hc:>16}')

    def show_a_row(nrow):
        name = Table_Fuels[nrow][0]
        try:
            print(f'{name:<32}', end='')
        except TypeError:
            print('')

        lhv = Table_Fuels[nrow][1]
        try:
            print(f'{lhv:>16}', end='')
        except TypeError:
            print('')

        hhv = Table_Fuels[nrow][2]
        try:
            print(f'{hhv:>16}', end='')
        except TypeError:
            print('')

        hc = Table_Fuels[nrow][3]
        try:
            print(f'{hc:>16,.2f}')
        except TypeError:
            print('')

    if complete:
        show_header()
        if row == 0:
            for n in range(len(Table_Fuels)):
                show_a_row(n)
        else:
            show_a_row(row)

    else:
        for n in range(len(Table_Fuels)):
            print('[ ', n + 1, ' ]:   ', Table_Fuels[n][0])


def complete_table():
    for n in range(len(Table_Fuels)):
        if (Table_Fuels[n][2] == '') and (Table_Fuels[n][3] == ''):
            pass
        elif Table_Fuels[n][3] == '':
            Table_Fuels[n][3] = 100 * (Table_Fuels[n][2] - Table_Fuels[n][1]) / (9 * 2.441)
        elif Table_Fuels[n][2] == '':
            Table_Fuels[n][2] = Table_Fuels[n][1] + 9 * 2.441 * Table_Fuels[n][3] / 100
        elif Table_Fuels[n][1] == '':
            Table_Fuels[n][1] = Table_Fuels[n][2] - 9 * 2.441 * Table_Fuels[n][3] / 100
        else:
            pass


def select_fuel(n, boiler=False):
    global Fuel_Mix
    global priceComparison
    print('\nSelected a fuel from the list to your analysis:\n')

    while True:
        show_list_fuels(False)
        print('[ ', len(Table_Fuels) + 1, ' ]:   ADD A NEW FUEL TO THE LIST')
        if boiler:
            print('[ ', len(Table_Fuels) + 2, ' ]:   USE A BINARY MIXTURE OF FUELS\n')
        else:
            print()

        if mixFuels:
            if n == 0:
                msg = 'Choose the first fuel: '
            else:
                msg = 'Choose the second fuel: '
        else:
            if n == 0:
                msg = 'Choose the fuel: '
            else:
                msg = f'Choose the fuel {n}: '

        fuel_selected = input_int(msg)

        if 1 <= fuel_selected <= len(Table_Fuels):
            name = Table_Fuels[fuel_selected - 1][0]
            price = input_limited_float('Fuel price ($/kg): ', 0, 100000, True, False) if priceComparison else 1.0

            if useHigher:
                try:
                    hhv = Table_Fuels[fuel_selected - 1][2] / price
                    hc = Table_Fuels[fuel_selected - 1][3]
                    lhv = 0.0
                    break
                except TypeError:
                    print("This fuel doesn't have a Higher Heating Value or hydrogen content registered. "
                          "So, it cannot be used here.")
            else:
                try:
                    lhv = Table_Fuels[fuel_selected - 1][1] / price
                    hhv = 0.0
                    hc = 0.0
                    break
                except TypeError:
                    print("This fuel doesn't have a Lower Heating Value registered. So it cannot be used here.")
        elif fuel_selected == len(Table_Fuels) + 1:
            add_fuel()
        elif fuel_selected == len(Table_Fuels) + 2 and boiler:
            create_mix_fuels()
            name, lhv, hhv, hc = '', 0, 0, 0
            break
        else:
            print('Not a valid option!')

    return name, lhv, hhv, hc


def create_mix_fuels():
    global Fuel_Mix
    global mixFuels
    mixFuels = True

    print("\nCreating a binary mixture of fuels is simple: you just need to choose 2 different fuels form the list.\n")

    Fuel_Mix[0][0], Fuel_Mix[0][1], Fuel_Mix[0][2], Fuel_Mix[0][3] = select_fuel(0)
    Fuel_Mix[1][0], Fuel_Mix[1][1], Fuel_Mix[1][2], Fuel_Mix[1][3] = select_fuel(1)


def add_fuel():
    name, lhv, hhv, hc = '', '', '', ''
    name = str(input("Insert fuel's name: "))

    while useHigher:
        print("\nWould you like to insert:\n"
              "[ 1 ]: Higher Heating Value (HHV) and Lower Heating Value (LHV)\n"
              "[ 2 ]: Higher Heating Value (HHV) and hydrogen content (%)\n"
              "[ 3 ]: Lower Heating Valuer (LHV) and hydrogen content (%)\n")

        option = input_int("Choose an option: ")

        if option == 1:
            hhv = input_float("Insert fuel's Higher Heating Value (MJ/kg): ")
            lhv = input_float("Insert fuel's Lower Heating Value (MJ/kg): ")
            break
        elif option == 2:
            hhv = input_float("Insert fuel's Higher Heating Value (MJ/kg): ")
            hc = input_limited_float("Insert fuel's hydrogen content (%): ", 0, 100, True, True)
            break
        elif option == 3:
            lhv = input_float("Insert fuel's Lower Heating Value (MJ/kg): ")
            hc = input_limited_float("Insert fuel's hydrogen content (%): ", 0, 100, True, True)
            break
        else:
            print('\nNot a valid option!\n')
    else:
        lhv = input_float("Insert fuel's Lower Heating Value (MJ/kg): ")

    Table_Fuels.append([name, lhv, hhv, hc])
    complete_table()


def create_slider(ax, label, valmin, valmax, valinit):
    return Slider(
        ax=ax,
        label=label,
        valmin=valmin,
        valmax=valmax,
        valinit=valinit
    )


def heat_vaporization_water(t):
    steam = Fluid(FluidsList.Water).dew_point_at_temperature(t)
    water = Fluid(FluidsList.Water).bubble_point_at_temperature(t)
    return (steam.enthalpy/1000 - water.enthalpy/1000)/1000


def h_steam_saturated(p):
    return Fluid(FluidsList.Water).dew_point_at_pressure(1000*p).enthalpy/1000


def h_steam_superheated(p, t):
    return Fluid(FluidsList.Water).with_state(
        Input.temperature(t),
        Input.pressure(1000*p)
    ).enthalpy/1000.0


def h_water_saturated(p, t):
    if useWaterPressure:
        water = Fluid(FluidsList.Water).bubble_point_at_pressure(1000*p)
    else:
        water = Fluid(FluidsList.Water).bubble_point_at_temperature(t)
    return water.enthalpy/1000.0


def higher_to_lower_hv(heating_value, hydrogen_content):
    return heating_value - heat_vaporization_water(25) * 9 * hydrogen_content/100.0


def lower_to_net_hv(heating_value, w, hc):
    if useHigher:
        return higher_to_lower_hv(heating_value, hc) * (1 - w/100.0) - heat_vaporization_water(25) * w/100.0
    else:
        return heating_value*(1 - w/100.0) - heat_vaporization_water(25) * w/100.0


def combustion_power(x1, e1, w1, hc1, e2, w2, hc2):
    return (x1/100.0) * lower_to_net_hv(e1, w1, hc1) + (1 - x1/100.0) * lower_to_net_hv(e2, w2, hc2)


def net_power(b, p_out, t_out, p_in, t_in):
    h_steam = h_steam_saturated(p_out)/1000.0 if saturatedSteam else h_steam_superheated(p_out, t_out)/1000.0
    h_water = h_water_saturated(p_in, t_in)/1000.0
    return h_steam - h_water/(1 - b/100.0)


def boiler_equation(m_steam, eff, x1, e1, w1, hc1, e2, w2, hc2, b, p_out, t_out, p_in, t_in):
    return 100 * (m_steam/eff) * net_power(b, p_out, t_out, p_in, t_in)/combustion_power(x1, e1, w1, hc1, e2, w2, hc2)


def efficiency_equation(m_steam, m_fuel, x1, e1, w1, hc1, e2, w2, hc2, b, p_out, t_out, p_in, t_in):
    return 100 * (m_steam/m_fuel) * \
           net_power(b, p_out, t_out, p_in, t_in)/combustion_power(x1, e1, w1, hc1, e2, w2, hc2)


def moisture_validation(w, heating_value):
    if w < 100*heating_value/(heating_value + heat_vaporization_water(25)):
        return True
    else:
        print('A fuel with this moisture percentage cannot produce energy to the boiler.')
        return False


def main_menu():
    while True:
        print("\nMain Menu:\n\n"
              "[ 0 ]: EXIT CALCULATOR\n"
              "[ 1 ]: Boiler Full Report\n"
              "[ 2 ]: Boiler's variables analysis\n"
              "[ 3 ]: Fuel analysis\n"
              "[ 4 ]: Settings\n")

        option = input_int('Choose a valid option: ')

        if option == 0:
            break
        elif option == 1:
            boiler_report_menu()
        elif option == 2:
            boiler_menu()
        elif option == 3:
            fuel_analysis_menu()
        elif option == 4:
            settings_menu()
        else:
            print('\nNot a valid option!\n')


def boiler_menu():
    global mixFuels, saturatedSteam
    mixFuels = False

    fueldata = boiler_fuel()

    while True:
        boiler_options()
        option = input_int('Choose a valid option: ')

        mode = operation_mode(option, fueldata[0], fueldata[1])

        if mode[0][0] == 'EXIT':
            break
        elif mode[0][0] == 'ERROR':
            print('Not a valid option!')
        else:
            mode = boiler_slider_declaration(mode)
            boiler_graphic(mode, fueldata[2], fueldata[3], fueldata[4], fueldata[5])


def boiler_fuel():
    fuel = select_fuel(0, True)
    if mixFuels:
        name1, name2, hc1, hc2 = Fuel_Mix[0][0], Fuel_Mix[1][0], Fuel_Mix[0][3], Fuel_Mix[1][3]
        if useHigher:
            enthalpy1, enthalpy2 = Fuel_Mix[0][2], Fuel_Mix[1][2]
        else:
            enthalpy1, enthalpy2 = Fuel_Mix[0][1], Fuel_Mix[1][1]
    else:
        name1, name2, hc1, hc2 = fuel[0], fuel[0], fuel[3], fuel[3]
        if useHigher:
            enthalpy1, enthalpy2 = fuel[2], fuel[2]
        else:
            enthalpy1, enthalpy2 = fuel[1], fuel[1]

    return name1, name2, enthalpy1, enthalpy2, hc1, hc2


def boiler_options():
    global mixFuels, useWaterPressure, saturatedSteam

    print("Choose the variable of analysis:\n")
    print("[ 0 ]: RETURN TO MAIN MENU")
    print("[ 1 ]: Boiler efficiency (%)")
    if mixFuels:
        print("[ 2 ]: Mass ratio of the mixture (%)")
    else:
        print("[ 2 ]: Fuel moisture (%)")
    if useWaterPressure:
        print("[ 3 ]: Feedwater absolute pressure (kPa)")
    else:
        print("[ 3 ]: Feedwater temperature (°C)")
    print("[ 4 ]: Steam mass flow (ton/h)")
    print("[ 5 ]: Steam absolute pressure (kPa)")
    if not saturatedSteam:
        print("[ 6 ]: Steam temperature (°C)\n")


def operation_mode(opt, name1, name2):
    global mixFuels, useWaterPressure, saturatedSteam
    mode = [['VARIABLE OF ANALYSIS', 0, 0],
            ['Boiler efficiency (%)', 1, 80],
            ['Steam mass flow (ton/h)', 1, 15],
            ['Blowdown rate (%)', 1, 5],
            [str(name1 + ' moisture (%)'), 1, 10],
            [str(name2 + ' moisture (%)'), 1, 10],
            [str('Mass ratio of ' + name1 + ' (%)'), 1, 100],
            ['Steam absolute pressure (kPa)', 1, 588],
            ['Steam temperature (°C)', 1, 200],
            ['Feedwater absolute pressure (kPa)', 1, 101.33],
            ['Feedwater temperature (°C)', 1, 100]]

    if not mixFuels:
        mode[5][1] = 0
        mode[6][1] = 0

    if saturatedSteam:
        mode[8][1] = 0

    if useWaterPressure:
        mode[10][1] = 0
    else:
        mode[9][1] = 0

    if opt == 0:
        mode[0][0] = 'EXIT'
    elif opt == 1:
        mode[1][1] = 2
        mode[0][1] = 1
        mode[0][0] = mode[1][0]
    elif opt == 2:
        if mixFuels:
            mode[6][1] = 2
            mode[0][1] = 6
            mode[0][0] = mode[6][0]
        else:
            mode[4][1] = 2
            mode[0][1] = 4
            mode[0][0] = mode[4][0]
    elif opt == 3:
        if useWaterPressure:
            mode[9][1] = 2
            mode[0][1] = 9
            mode[0][0] = mode[9][0]
        else:
            mode[10][1] = 2
            mode[0][1] = 10
            mode[0][0] = mode[10][0]
    elif opt == 4:
        mode[2][1] = 2
        mode[0][1] = 2
        mode[0][0] = mode[2][0]
    elif opt == 5:
        mode[7][1] = 2
        mode[0][1] = 7
        mode[0][0] = mode[7][0]
    elif opt == 6 and not saturatedSteam:
        mode[8][1] = 2
        mode[0][1] = 8
        mode[0][0] = mode[8][0]
    else:
        mode[0][0] = 'ERROR'

    return mode


def boiler_slider_declaration(mode):
    global sliders
    sliders = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    y = 0.60

    if mode[1][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[0] = create_slider(ax_slid, mode[1][0], 1, 100, mode[1][2])
        y -= 0.05
    if mode[2][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[1] = create_slider(ax_slid, mode[2][0], 0, 50, mode[2][2])
        y -= 0.05
    if mode[3][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[2] = create_slider(ax_slid, mode[3][0], 0, 10, mode[3][2])
        y -= 0.05
    if mode[4][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[3] = create_slider(ax_slid, mode[4][0], 0, 90, mode[4][2])
        y -= 0.05
    if mode[5][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[4] = create_slider(ax_slid, mode[5][0], 0, 90, mode[5][2])
        y -= 0.05
    if mode[6][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[5] = create_slider(ax_slid, mode[6][0], 0, 100, mode[6][2])
        y -= 0.05
    if mode[7][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[6] = create_slider(ax_slid, mode[7][0], 101.33, 5000, mode[7][2])
        y -= 0.05
    if mode[8][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[7] = create_slider(ax_slid, mode[8][0], 100, 800, mode[8][2])
        y -= 0.05
    if mode[9][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[8] = create_slider(ax_slid, mode[9][0], 1, 5000, mode[9][2])
        y -= 0.05
    if mode[10][1] == 1:
        ax_slid = plt.axes([0.45, y, 0.45, 0.03])
        sliders[9] = create_slider(ax_slid, mode[10][0], 0, 310, mode[10][2])

    return mode


def boiler_graphic(mode, enthalpy1, enthalpy2, hc1, hc2):
    global mixFuels, saturatedSteam
    global sliders

    x_values, y_values = [], []
    parameters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    label_x = mode[0][0]

    for n in range(10):
        parameters[n] = sliders[n].val if mode[n+1][1] == 1 else mode[n+1][2]

    if mode[0][1] == 1:
        x_values = list(np.linspace(1, 100, 50))
    elif mode[0][1] == 2:
        x_values = list(np.linspace(0, 50, 50))
    elif mode[0][1] == 4:
        x_values = list(np.linspace(0, 90, 50))
    elif mode[0][1] == 6:
        x_values = list(np.linspace(0, 100, 50))
    elif mode[0][1] == 7:
        x_values = list(np.linspace(101.33, 5000, 50))
    elif mode[0][1] == 8:
        x_values = list(np.linspace(100, 800, 50))
    elif mode[0][1] == 9:
        x_values = list(np.linspace(1, 5000, 50))
    elif mode[0][1] == 10:
        x_values = list(np.linspace(0, 310, 50))

    for n in range(len(x_values)):
        parameters[(mode[0][1]-1)] = x_values[n]
        y = boiler_equation(
            eff=parameters[0],
            m_steam=parameters[1],
            b=parameters[2],
            w1=parameters[3],
            w2=parameters[4],
            x1=parameters[5],
            p_out=parameters[6],
            t_out=parameters[7],
            p_in=parameters[8],
            t_in=parameters[9],
            e1=enthalpy1,
            e2=enthalpy2,
            hc1=hc1,
            hc2=hc2
        )
        y_values.append(y)

    fig, ax = plt.subplots()
    plt.grid()
    line, = plt.plot(x_values, y_values)
    ax.set_xlabel(label_x)

    def update(val):
        global y_values
        y_values = []
        for i in range(10):
            parameters[i] = sliders[i].val if mode[i + 1][1] == 1 else mode[i + 1][2]

        for j in range(len(x_values)):
            parameters[(mode[0][1] - 1)] = x_values[j]
            current_y = boiler_equation(
                eff=parameters[0],
                m_steam=parameters[1],
                b=parameters[2],
                w1=parameters[3],
                w2=parameters[4],
                x1=parameters[5],
                p_out=parameters[6],
                t_out=parameters[7],
                p_in=parameters[8],
                t_in=parameters[9],
                e1=enthalpy1,
                e2=enthalpy2,
                hc1=hc1,
                hc2=hc2
            )
            y_values.append(current_y)

        line.set_ydata(y_values)
        fig.canvas.draw_idle()

    for n in range(10):
        if mode[n+1][1] == 1:
            sliders[n].on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    button_reset = Button(resetax, 'Reset', hovercolor='0.975')

    def reset(event):
        for i in range(10):
            if mode[i+1][1] == 1:
                sliders[i].reset()

    button_reset.on_clicked(reset)

    rescaleax = plt.axes([0.5, 0.025, 0.1, 0.04])
    button_rescale = Button(rescaleax, 'Rescale', hovercolor='0.975')

    def rescale(event):
        ax.margins(x=0)
        ax.relim()
        ax.autoscale()
        ax.autoscale_view()

        plt.subplots_adjust(bottom=0.25)
        plt.show()

    button_rescale.on_clicked(rescale)

    ax.set_ylabel('Fuel consumption (ton/h)')
    ax.margins(x=0)
    ax.set_ylim([0, 100])

    plt.subplots_adjust(bottom=0.25)
    plt.show()


def boiler_report_menu():
    while True:
        print('\nReport Menu:\n'
              '[ 0 ]: RETURN TO MAIN MENU\n'
              '[ 1 ]: Insert data from a working boiler '
              '(calculate the boiler operational efficiency)\n'
              '[ 2 ]: Insert data from a hypothetical boiler '
              '(calculate the required fuel mass flow for the boiler to work)\n')

        option = input_int('Choose a valid option: ')

        if option == 0:
            break
        elif option == 1:
            boiler_full_report('efficiency')
        elif option == 2:
            boiler_full_report('fuel mass flow')
        else:
            print('\nNot a valid option!\n')


def boiler_full_report(unknown_variable):
    name1, name2, e1, e2, hc1, hc2 = boiler_fuel()

    while True:
        w1 = input_limited_float(f'Insert {name1} moisture (%): ', 0, 100, True, False)
        fuel_generates_energy = moisture_validation(w1, e1)
        w2 = 0
        if fuel_generates_energy:
            break
    if mixFuels:
        while True:
            w2 = input_limited_float(f'Insert {name2} moisture (%): ', 0, 100, True, False)
            fuel_generates_energy = moisture_validation(w2, e2)
            if fuel_generates_energy:
                break
        x1 = input_limited_float(f'Insert mass ratio of {name1}: ', 0, 100, False, False)
    else:
        x1 = 100

    if unknown_variable == 'fuel mass flow':
        eff = input_limited_float("Insert boiler's efficiency (%): ", 0, 100, False, False)
        bd_rate = input_limited_float("Insert blowdown rate (%): ", 0, 100, False, False)
    else:
        m_fuel = input_limited_float("Insert fuel mass flow (ton/h): ", 0, 50, False, True)
        m_water = input_limited_float("Insert feedwater mass flow (ton/h): ", 0, 50, False, True)

    if useWaterPressure:
        p_in = input_limited_float("Insert feedwater pressure (kPa): ", 0, 10000, True, False)
        t_in = Fluid(FluidsList.Water).bubble_point_at_pressure(1000*p_in).temperature
    else:
        t_in = input_limited_float("Insert feedwater temperature (°C): ", 0, 310, False, False)
        p_in = Fluid(FluidsList.Water).bubble_point_at_temperature(t_in).pressure/1000

    if unknown_variable == 'fuel mass flow':
        m_steam = input_float("Insert steam mass flow (ton/h): ")
        m_water = m_steam / (1 - bd_rate/100)
    else:
        m_steam = input_limited_float("Insert steam mass flow (ton/h): ", 0, m_water, False, True)
        bd_rate = 100 * (m_water - m_steam) / m_water

    p_out = input_limited_float("Insert steam pressure (kPa): ", p_in, 10000, False, True)
    t_out = Fluid(FluidsList.Water).dew_point_at_pressure(1000*p_out).temperature if saturatedSteam \
        else input_limited_float("Insert steam temperature (°C): ", t_in, 800, False, True)

    fuel_specific_enthalpy = combustion_power(x1, e1, w1, hc1, e2, w2, hc2)
    if unknown_variable == 'fuel mass flow':
        m_fuel = boiler_equation(m_steam, eff, x1, e1, w1, hc1, e2, w2, hc2, bd_rate, p_out, t_out, p_in, t_in)
    else:
        eff = efficiency_equation(m_steam, m_fuel, x1, e1, w1, hc1, e2, w2, hc2, bd_rate, p_out, t_out, p_in, t_in)

    general_section_report(bd_rate, eff)
    fuel_section_report(name1, name2, e1, e2, hc1, hc2, w1, w2, x1, fuel_specific_enthalpy, m_fuel)
    water_section_report(m_water, p_in, t_in)
    steam_section_report(m_steam, p_out, t_out)


def title_section_report(title):
    print(60*'=')
    print('==   ', f'{title: ^48}', '   ==')
    print(60*'=')


def general_section_report(bd_rate, eff):
    title_section_report('BOILER OPERATIONAL INFORMATION')
    print('==   Boiler efficiency: ', f'{eff: >28}', '%   ==')
    print('==   Blowdown Rate: ', f'{bd_rate: >32}', '%   ==')
    print(60*'=')
    print()


def fuel_section_report(name1, name2, e1, e2, hc1, hc2, w1, w2, x1, enthalpy, m_fuel):
    title_section_report('FUEL INFORMATION')
    if mixFuels:
        print('==   First Fuel: ', f'{name1: >36}', '   ==')
        if useHigher:
            print('==   Higher Heating Value: ', f'{e1: >21,.2f}', 'MJ/kg   ==')
            print('==   Hydrogen content: ', f'{hc1: >29,.2f}', '%   ==')
        else:
            print('==   Lower Heating Value: ', f'{e1: >22,.2f}', 'MJ/kg   ==')
        print('==   Moisture: ', f'{w1: >37,.2f}', '%   ==')
        print('==   Mass ratio: ', f'{x1: >35,.2f}', '%   ==')
        print(60*'=')
        print('==   Second Fuel: ', f'{name2: >35}', '   ==')
        if useHigher:
            print('==   Higher Heating Value: ', f'{e2: >21,.2f}', 'MJ/kg   ==')
            print('==   Hydrogen content: ', f'{hc2: >29,.2f}', '%   ==')
        else:
            print('==   Lower Heating Value: ', f'{e1: >22,.2f}', 'MJ/kg   ==')
        print('==   Moisture: ', f'{w2: >37,.2f}', '%   ==')
        print('==   Mass ratio: ', f'{(100-x1): >35,.2f}', '%   ==')
    else:
        print('==   Fuel: ', f'{name1: >42}', '   ==')
        if useHigher:
            print('==   Higher Heating Value: ', f'{e1: >21,.2f}', 'MJ/kg   ==')
            print('==   Hydrogen content: ', f'{hc1: >29,.2f}', '%   ==')
        else:
            print('==   Lower Heating Value: ', f'{e1: >22,.2f}', 'MJ/kg   ==')
        print('==   Moisture: ', f'{w1: >37,.2f}', '%   ==')
    print(60*'=')
    print('==   Specific Enthalpy: ', f'{enthalpy: >24,.2f}', 'MJ/kg   ==')
    print("==   Mass flow (required): ", f'{m_fuel: >21,.2f}', 'ton/h   ==')
    energy_flow = 1000*m_fuel*enthalpy/3600
    print('==   Energy Flow: ', f'{energy_flow: >33,.2f}', 'MW   ==')
    print(60 * '=')
    print()


def water_section_report(m_water, p_in, t_in):
    energy = h_water_saturated(p_in, t_in) / 1000
    energy_flow = 1000 * m_water * energy / 3600

    title_section_report('FEEDWATER INFORMATION')
    print('==   Mass flow (required): ', f'{m_water: >21,.2f}', 'ton/h   ==')
    print('==   Pressure: ', f'{p_in: >35,.2f}', 'kPa   ==')
    print('==   Temperature: ', f'{t_in: >33,.2f}', '°C   ==')
    print('==   Specific Enthalpy: ', f'{energy: >24,.2f}', 'MJ/kg   ==')
    print('==   Energy Flow: ', f'{energy_flow: >33,.2f}', 'MW   ==')
    print(60 * '=')
    print()


def steam_section_report(m_steam, p_out, t_out):
    phase = 'Saturated Steam' if saturatedSteam else 'Superheated Steam'
    energy = h_steam_saturated(p_out)/1000 if saturatedSteam else h_steam_superheated(p_out, t_out)/1000
    energy_flow = 1000 * m_steam * energy / 3600

    title_section_report('STEAM INFORMATION')
    print('==   Mass flow (desired): ', f'{m_steam: >22,.2f}', 'ton/h   ==')
    print('==   Pressure: ', f'{p_out: >35,.2f}', 'kPa   ==')
    print('==   Temperature: ', f'{t_out: >33,.2f}', '°C   ==')
    print('==   Phase: ', f'{phase: >42}', '  ==')
    print('==   Specific Enthalpy: ', f'{energy: >24,.2f}', 'MJ/kg   ==')
    print('==   Energy Flow: ', f'{energy_flow: >33,.2f}', 'MW   ==')
    print(60 * '=')
    print()


def fuel_analysis_menu():
    global useHigher
    global priceComparison
    global mixFuels
    type_hv = 'Higher' if useHigher else 'Lower'

    while True:
        mixFuels = False
        priceComparison = False
        print('\nFuel Analysis Menu:\n'
              '[ 0 ]: RETURN TO MAIN MENU\n'
              f'[ 1 ]: Compare the {type_hv} Heating Values of different fuels\n'
              '[ 2 ]: Compare the economic performance of different fuels\n'
              f'[ 3 ]: Evaluate the {type_hv} Heating Value of a binary mixture of fuels\n'
              '[ 4 ]: Evaluate the economic performance of a binary mixture of fuels')

        option = input_int('Choose a valid option: ')
        priceComparison = True if (option == 2 or option == 4) else False

        if option == 0:
            break
        elif option == 1 or option == 2:
            compare_fuels(type_hv)
        elif option == 3 or option == 4:
            create_mix_fuels()
            evaluate_mix_fuels(type_hv)
        else:
            print('\nNot a valid option!\n')


def compare_fuels(type_hv):
    numb_fuels = input_int('How many fuels do you want to compare? ')
    current_numb = 1
    moisture_range = np.linspace(0, 100)
    ymaxaxis = 0

    show_list_fuels(False)
    print('[ ', len(Table_Fuels) + 1, ' ]: ADD A NEW FUEL TO THE LIST')

    while current_numb <= numb_fuels:
        Fuel_Mix[0][0], Fuel_Mix[0][1], Fuel_Mix[0][2], Fuel_Mix[0][3] = select_fuel(current_numb)
        enthalpy = Fuel_Mix[0][2] if useHigher else Fuel_Mix[0][1]
        current_numb += 1

        ymaxaxis = 1.1 * enthalpy if (1.1 * enthalpy > ymaxaxis) else ymaxaxis
        plt.plot(moisture_range,
                 combustion_power(50, enthalpy, moisture_range, Fuel_Mix[0][3],
                                  enthalpy, moisture_range, Fuel_Mix[0][3]), label=Fuel_Mix[0][0])

    plt.xlabel('Moisture (%)')
    ylabel = 'Economic performance (MJ / $)' if priceComparison else f'{type_hv} Heating Value (MJ / kg)'
    plt.ylabel(ylabel)

    plt.legend(loc='upper right')
    plt.axis([0, 100, 0, ymaxaxis])
    plt.grid()
    plt.show()


def evaluate_mix_fuels(type_hv):
    global Fuel_Mix

    label1, label2 = str(f'Moisture - {Fuel_Mix[0][0]} (%)'), str(f'Moisture - {Fuel_Mix[1][0]} (%)')
    energy1 = Fuel_Mix[0][2] if useHigher else Fuel_Mix[0][1]
    energy2 = Fuel_Mix[1][2] if useHigher else Fuel_Mix[1][1]
    hc1, hc2 = Fuel_Mix[0][3] if useHigher else 0.0, Fuel_Mix[1][3] if useHigher else 0.0
    ymaxaxis = 1.1 * energy1 if (energy1 > energy2) else 1.1 * energy2

    ax1 = plt.axes([0.45, 0.15, 0.45, 0.03])
    slider1 = create_slider(ax1, label1, 0, 100, 10)
    ax2 = plt.axes([0.45, 0.20, 0.45, 0.03])
    slider2 = create_slider(ax2, label2, 0, 100, 10)

    mass_ratio = np.linspace(0, 100)

    fig, ax = plt.subplots()
    plt.grid()
    line, = plt.plot(mass_ratio, combustion_power(mass_ratio, energy1, 10, hc1, energy2, 10, hc2))
    ax.set_xlabel('Mass Ratio of ' + Fuel_Mix[0][0] + ' (%)')

    def update(val):
        line.set_ydata(combustion_power(mass_ratio, energy1, slider1.val, hc1, energy2, slider2.val, hc2))
        fig.canvas.draw_idle()

    slider1.on_changed(update)
    slider2.on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(resetax, 'Reset', hovercolor='0.975')

    def reset(event):
        slider1.reset()
        slider2.reset()

    button.on_clicked(reset)

    rescaleax = plt.axes([0.5, 0.025, 0.1, 0.04])
    button_rescale = Button(rescaleax, 'Rescale', hovercolor='0.975')

    def rescale(event):
        ax.margins(x=0)
        ax.relim()
        ax.autoscale()
        ax.autoscale_view()

        plt.subplots_adjust(bottom=0.25)
        plt.grid(True)
        plt.draw()
        plt.show()

    button_rescale.on_clicked(rescale)

    ylabel = 'Economic performance (kJ/$)' if priceComparison else f'{type_hv} Heating Value (MJ/kg)'
    ax.set_ylabel(ylabel)

    ax.margins(x=0)
    ax.set_ylim([0, ymaxaxis])

    plt.subplots_adjust(bottom=0.25)
    plt.show()


def settings_menu():
    global useHigher, useWaterPressure, saturatedSteam

    while True:
        print('\nSettings Menu:\n'
              '[ 0 ]: RETURN TO MAIN MENU\n'
              '[ 1 ]: Show list of registered fuels\n'
              '[ 2 ]: Register a new fuel\n'
              '[ 3 ]: Update a registered fuel\n'
              '[ 4 ]: Change the Heating Value method of calculation (Lower or Higher)\n'
              '[ 5 ]: Change the default parameter for the feedwater (pressure or temperature)\n'
              '[ 6 ]: Change the thermodynamic state of the output steam (Superheated steam or Saturated steam)\n')

        option = input_int('Choose a valid option: ')

        if option == 0:
            break
        elif option == 1:
            show_list_fuels(True)
        elif option == 2:
            add_fuel()
        elif option == 3:
            update_fuel()
        elif option == 4:
            useHigher = hv_method()
        elif option == 5:
            useWaterPressure = fw_input()
        elif option == 6:
            saturatedSteam = steam_state()
        else:
            print('\nNot a valid option!\n')


def hv_method():
    type_method = 'Higher Heating Value' if useHigher else 'Lower Heating Value'
    while True:
        print(f"\nThe calculator is set to use the {type_method}'s equations. "
              "You may change the method of calculation:\n"
              "[ 1 ]: Use Lower Heating Values' (LHV) equations.\n"
              "[ 2 ]: Use Higher Heating Values' (HHV) equations.\n"
              "ATTENTION: Select Method 2 only when you know the hydrogen content of the fuel.\n")

        method = int(input('Choose a valid method: '))

        if method == 1:
            print('\nMethod selected: Lower Heating Values\n')
            return False
        if method == 2:
            print('\nMethod selected: Higher Heating Values\n')
            return True
        else:
            print('\nNot a valid method!\n')


def fw_input():
    type_input = 'pressure' if useWaterPressure else 'temperature'
    while True:
        print("\nThe boiller's feedwater is a saturated liquid."
              "It's thermodynamic state variables can be determined by using pressure or temperature.\n"
              f"The calculator is set to use {type_input}. Choose the parameter you would like to use:\n"
              "[ 1 ]: Feedwater's enthalpy is calculated using Pressure input (kPa).\n"
              "[ 2 ]: Feedwater's enthalpy is calculated using Temperature input (°C).\n")

        method = int(input('Choose a valid parameter: '))

        if method == 1:
            print('\nParameter selected: Pressure\n')
            return True
        if method == 2:
            print('\nParameter selected: Temperature\n')
            return False
        else:
            print('\nNot a valid parameter!\n')


def steam_state():
    type_state = "Saturated Steam" if saturatedSteam else "Superheated Steam"
    while True:
        print(f"\nThe Boiler Energy Calculator is set to produce {type_state}."
              "Choose the thermodynamic state of the steam produced:\n"
              "[ 1 ]: Superheated Steam (needs pressure and temperature as input to calculate enthalpy).\n"
              "[ 2 ]: Saturated Steam (needs only pressure as input to calculate enthalpy).\n")

        method = int(input('Choose a valid state: '))

        if method == 1:
            print('\nThermodynamic state selected: Superheated Steam\n')
            return False
        if method == 2:
            print('\nThermodynamic state selected: Saturated Steam\n')
            return True
        else:
            print('\nNot a valid option!\n')


def update_fuel():
    while True:
        print("Which fuel you want to update?\n")
        print("[ 0 ]: RETURN TO SETTINGS MENU")
        show_list_fuels(False)

        n_fuel = input_int("\nChoose a fuel: ")

        if n_fuel == 0:
            break
        elif n_fuel <= len(Table_Fuels):
            show_list_fuels(True, n_fuel)

            while True:
                print("\nWhat do you want to update?\n"
                      "[ 0 ]: NONE\n"
                      "[ 1 ]: Fuel's name\n"
                      "[ 2 ]: Fuel's Lower Heating Value (LHV)\n"
                      "[ 3 ]: Fuel's Higher Heating Valuer (HHV)\n"
                      "[ 4 ]: Fuel's hydrogen content (%)\n")

                change = input_int("Choose an option: ")

                if change == 0:
                    break
                elif change == 1:
                    Table_Fuels[n_fuel - 1][0] = str(input("Insert new fuel's name: "))
                elif change == 2:
                    Table_Fuels[n_fuel - 1][1] = input_float("Insert new fuel's LHV: ")
                elif change == 3:
                    Table_Fuels[n_fuel - 1][2] = input_float("Insert new fuel's HHV: ")
                elif change == 4:
                    Table_Fuels[n_fuel - 1][3] = \
                        input_limited_float("Insert new fuel's hydrogen content (%): ", 0, 100, True, True)
                else:
                    print('\nNot a valid option!\n')

        else:
            print('\nNot a valid option!\n')


useWaterPressure = True
saturatedSteam = False
useHigher = False
mixFuels = False
Fuel_Mix = [['', 0.0, 0.0, 0.0],
            ['', 0.0, 0.0, 0.0]]
priceComparison = False

complete_table()

print('\n\nWelcome to the Boiler Energy Calculator!\n\n'
      'This is a digital tool that allows any user to perform a basic thermal analysis for Boilers.\n'
      'In addition, this calculator also allows the user to evaluate and compare different fuels and even a '
      'binary fuel mix (the most common in the industry).\n'
      'The Boiler Energy Calculator was created with the intention to '
      'provide a tool to easily perform analyzes of biomass fuels in boilers for the industry.\n')

print('\nThe Boiler Energy Calculator can work with Lower Heating Values or Higher Heating Values, \n'
      'Superheated Steam or Saturated Steam, Pressure or Temperature as the input for the feedwater.\n'
      'The default configuration is: Lower Heating Values, Superheated Steam, Feedwater Pressure as input.\n'
      'You can alter all those options in "Settings".')

main_menu()

print('\n\nGoodbye, have a nice day!')
