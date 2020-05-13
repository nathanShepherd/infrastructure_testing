import matplotlib.pyplot as plt
import numpy as np

def gen_time_series(shape, limits=(0, 10)):
    x = np.arange(shape)
    y = np.random.uniform(limits[0], limits[1], shape)
    return x, sorted(y)

plt.style.use('ggplot')
#plt.style.use('fivethirtyeight')

def line_plot(x, y, title, xlabel='x', ylabel='y',
                 grid=False, fill=True):
    plt.plot(x, y,
                 label='Y',
                 color='k',
                 linestyle='--', # or ls	[ '-' | '--' | '-.' | ':' | 'steps' | ...]                 
                 #linewidth=1,
                 #marker=2    # denotes pt [ '+' | ',' | '.' | '1' | '2' | '3' | '4' ]
                                         # '^k' --> black triangles
                )
    
    plt.grid(grid,
                 which='major',
                 axis='both'
                 )
    if fill:
        plt.fill_between(x, y, label='Below',
                                 #y2=0, # lower threshold
                                 #where=() # cond --> (y > y2)
                                 color='blue',
                                 alpha=0.2 #transparency
                                 
                                 )
    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    
def stack_figures(X, Y, shape=(2, 1), ylabel=['y1', 'y2'], xlabel=['x']):
    if shape[0] * shape[1] != len(Y):
        raise NameError('Length of Y must be num of subplts')
    fig, ax = plt.subplots(shape[0])
    
    plt_num = 0
    for row in range(1, shape[0] + 1):
        #for col in range(1, shape[1] + 1):
        for axes in ax:
            axes.plot(X[plt_num], Y[plt_num])
            '''
            print(row, col, plt_num)
            plt.subplot(shape[0], shape[1], plt_num + 1) # = (nRows, nCols, plt_num)
            plt.plot(X[plt_num], Y[plt_num])
            '''
            plt_num += 1
            

def example_bar_plot_offset():
    x_idx = np.arange(10)
    x, y1 = gen_time_series(10)
    _, y2 = gen_time_series(10)
    # Note: For horizantal bar use plt.barh()
    width = 0.3
    plt.bar(x_idx, y1,
            width=width, color='b', label='y1')
    plt.bar(x_idx + width, y2,
            width=width, color='g', label='y2')

    plt.xticks(ticks=x_idx, label=x)
    plt.legend()
    plt.show()
    
def main_line_examples():
    x, y = gen_time_series(10)
    x2, y2 = gen_time_series(10)
    stack_figures([x, x2], [y, y2])
    
    #line_plot(x, y, 'Series', grid=True)
    plt.show()

if __name__ == "__main__":
    main_line_examples()
    #example_bar_plot_offset()
    
    
    
