from inputparser import Parser
from program import normalize_program
from recurrences.rec_builder import RecBuilder
from symengine.lib.symengine_wrapper import sympify
from stability_analysis import NumericStabilityAnalyzer

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from progress.bar import Bar


def get_rho(strategy, ps=0.0, pc=0.0, pa=0.0):
    file_path = f"../benchmarks/control_theory/ball_beam/{strategy}.prob"
    program = Parser().parse_file(file_path)
    for assign in program.initial:
        if str(assign.variable) == "ps":
            assign.polynomials = [sympify(ps)]
        if str(assign.variable) == "pc":
            assign.polynomials = [sympify(pc)]
        if str(assign.variable) == "pa":
            assign.polynomials = [sympify(pa)]

    program = normalize_program(program)

    rec_builder = RecBuilder(program)
    recurrences = rec_builder.get_recurrences(
        "x1", "x2", "x3", "x1**2", "x2**2", "x3**2"
    )

    analyzer = NumericStabilityAnalyzer(recurrences)
    return analyzer.get_rho()


def compute_single_variations(strategy):
    # vary ps
    ps_data = []
    with Bar("Varying ps ... ") as bar:
        for ps in np.arange(0, 1, 0.01):
            ps_data.append(get_rho(strategy, ps=ps))
            bar.next()
    print(f"ps data for {strategy}:")
    print(ps_data)

    # vary pc
    pc_data = []
    with Bar("Varying pc ... ") as bar:
        for pc in np.arange(0, 1, 0.01):
            pc_data.append(get_rho(strategy, pc=pc))
            bar.next()
    print(f"pc data for {strategy}:")
    print(pc_data)

    # vary pa
    pa_data = []
    with Bar("Varying pa ... ") as bar:
        for pa in np.arange(0, 1, 0.01):
            pa_data.append(get_rho(strategy, pa=pa))
            bar.next()
    print(f"pa data for {strategy}:")
    print(pa_data)


def compute_double_variations(strategy):
    density = 0.01
    xs = np.arange(0, 1, density)
    ys = np.arange(0, 1, density)
    xs, ys = np.meshgrid(xs, ys)
    zs = np.zeros(xs.shape)
    with Bar("Varying pc and ps ...", max=int((1 / density) ** 2)) as bar:
        for i in range(zs.shape[0]):
            for j in range(zs.shape[1]):
                pc = xs[i, j]
                ps = ys[i, j]
                zs[i, j] = get_rho(strategy, pc=pc, ps=ps)
                bar.next()
    print("2D values:")
    print(zs.tolist())


def plot_fig6():
    # Kill and Zero plot
    ps_data_kill_zero = [
        0.9978984860292592,
        0.9978984862817318,
        0.9978984865393534,
        0.9978984868022858,
        0.9978984870707013,
        0.9978984873447672,
        0.9978984876246627,
        0.9978984879105776,
        0.9978984882027102,
        0.9978984885012605,
        0.9978984888064465,
        0.9978984891184925,
        0.9978984894376304,
        0.9978984897641039,
        0.9978984900981687,
        0.9978984904400983,
        0.997898490790167,
        0.9978984911486719,
        0.9978984915159202,
        0.9978984918922374,
        0.9978984922779635,
        0.9978984926734559,
        0.9978984930790898,
        0.9978984934952583,
        0.9978984939223797,
        0.9978984943608907,
        0.9978984948112563,
        0.9978984952739571,
        0.9978984957495161,
        0.9978984962384689,
        0.9978984967413932,
        0.9978984972588949,
        0.9978984977916199,
        0.9978984983402501,
        0.9978984989055008,
        0.9978984994881483,
        0.9978985000890029,
        0.9978985007089362,
        0.997898501348865,
        0.9978985020097788,
        0.9978985026927241,
        0.9978985033988178,
        0.9978985041292661,
        0.9978985048853428,
        0.9978985056684271,
        0.997898506479988,
        0.9978985073216065,
        0.9978985081949873,
        0.9978985091019632,
        0.9978985100445085,
        0.9978985110247592,
        0.9978985120450219,
        0.997898513107799,
        0.997898514215805,
        0.9978985153719862,
        0.9978985165795626,
        0.9978985178420263,
        0.9978985191632185,
        0.9978985205473302,
        0.9978985219989677,
        0.9978985235231876,
        0.9978985251255823,
        0.9978985268123244,
        0.9978985285902459,
        0.9978985304669554,
        0.9978985324509151,
        0.9978985345515892,
        0.9978985367795916,
        0.9978985391468598,
        0.997898541666876,
        0.9978985443549092,
        0.9978985472283517,
        0.9978985503070611,
        0.9978985536138556,
        0.9978985571750534,
        0.9978985610211909,
        0.9978985651878864,
        0.9978985697169624,
        0.9978985746578349,
        0.9978985800693504,
        0.9978985860221151,
        0.9978985926016063,
        0.9986281596844219,
        1.005814579163735,
        1.0131157921056069,
        1.0203442696626326,
        1.0274517936122698,
        1.0344084590943294,
        1.0411871515029416,
        1.0477579183109071,
        1.0540846614018,
        1.0601218552238083,
        1.0658100856500947,
        1.071069080399318,
        1.075785880940787,
        1.0797931012490305,
        1.082824812325663,
        1.084413875174669,
        1.0835969881279695,
        1.0776664649891043,
    ]
    pc_data_kill_zero = [
        0.9978984860292592,
        0.9979123705259259,
        0.9979266402895767,
        0.9979412795310291,
        0.9979562730754816,
        0.9979716063452087,
        0.9979872653417252,
        0.9980032366276284,
        0.9980195073082606,
        0.9980360650133242,
        0.9980528978785647,
        0.9980699945275785,
        0.9980873440538651,
        0.9981049360031801,
        0.9981227603562149,
        0.9981408075116717,
        0.9981590682697692,
        0.9981775338161819,
        0.9981961957064579,
        0.9982150458509048,
        0.9982340764999846,
        0.998253280230179,
        0.9982726499303743,
        0.9982921787887128,
        0.9983118602799553,
        0.9983316881533045,
        0.9983516564207165,
        0.9983717593456556,
        0.9983919914323297,
        0.9984123474153322,
        0.9984328222497144,
        0.9984534111014983,
        0.9984741093385603,
        0.9984949125219091,
        0.9985158163973288,
        0.9985368168874046,
        0.9985579100838573,
        0.9985790922402277,
        0.998600359764895,
        0.998621709214359,
        0.998643137286847,
        0.9986646408161951,
        0.9986862167659909,
        0.9987078622239691,
        0.9987295743966583,
        0.9987513506042712,
        0.9987731882757953,
        0.9987950849443166,
        0.9988170382425379,
        0.9988390458984995,
        0.9988611057314775,
        0.998889801846288,
        0.9991029900723533,
        0.9993175823848738,
        0.9995335935251446,
        0.9997510354728203,
        1.0000709785178143,
        1.000514402587103,
        1.000961081224321,
        1.0014110305645458,
        1.0018642597894931,
        1.0023207689777776,
        1.002780547252751,
        1.0032435709528833,
        1.003709801696857,
        1.0041791842675596,
        1.004651644257645,
        1.0051270854247445,
        1.0056053867026677,
        1.0060863988091193,
        1.0065699403806903,
        1.0070557935525146,
        1.0075436988821167,
        1.0080333494939708,
        1.0085243842911327,
        1.009016380041351,
        1.009508842093565,
        1.0100011934129225,
        1.010492761531483,
        1.0109827628891508,
        1.0114702838713054,
        1.0119542576172171,
        1.012433435346025,
        1.0129063504804134,
        1.0133712731694207,
        1.0138261518067673,
        1.0142685366192825,
        1.0146954780392607,
        1.0151033888105823,
        1.015487852584605,
        1.0158433511956724,
        1.0161628640048554,
        1.0164372575413192,
        1.0166543138742006,
        1.0167970970520674,
        1.0168410075738814,
        1.016747950515479,
        1.0164531489575306,
        1.01582843291876,
        1.0145303757667365,
    ]
    pa_data_kill_zero = [
        0.9978984860292592,
        0.9978982337083446,
        0.9978979761880671,
        0.9978977133060668,
        0.9978974448931709,
        0.9978971707730036,
        0.9978968907616139,
        0.9978966046670679,
        0.9978963122889885,
        0.9978960134181214,
        0.997895707835802,
        0.9978953953134525,
        0.9978950756119886,
        0.9978947484812202,
        0.997894413659195,
        0.997894070871516,
        0.9978937198305657,
        0.9978933602347186,
        0.9978929917674745,
        0.9978926140965342,
        0.9978922268727923,
        0.9978918297292716,
        0.9978914222799463,
        0.9978910041185264,
        0.9978905748170666,
        0.9978901339245434,
        0.9978896809652443,
        0.9978892154370843,
        0.9978887368097438,
        0.9978882445226441,
        0.99788773798278,
        0.9978872165623165,
        0.9978866795960197,
        0.997886126378423,
        0.9978855561607295,
        0.9978849681474398,
        0.9978843614926691,
        0.9978837352960728,
        0.997883088598421,
        0.9978824203766744,
        0.9978817295386222,
        0.9978810149169189,
        0.9978802752625244,
        0.9978795092374247,
        0.9978787154065868,
        0.9978778922289826,
        0.9978770380476619,
        0.9978761510786117,
        0.9978752293983723,
        0.9978742709301459,
        0.9978732734282134,
        0.9978722344604253,
        0.9978711513884513,
        0.9978700213454871,
        0.9978688412109997,
        0.997867607582047,
        0.9978663167406195,
        0.9978649646163605,
        0.9978635467438584,
        0.9978620582135854,
        0.9978604936153551,
        0.9978588469728988,
        0.9978571116679721,
        0.9978552803518939,
        0.9978533448420802,
        0.9978512960005177,
        0.9978491235903731,
        0.9978468161060401,
        0.9978443605707171,
        0.9978417422940145,
        0.9978389445801669,
        0.9978359483746516,
        0.9978327318335983,
        0.9978292697955998,
        0.9978255331292064,
        0.9978214879207145,
        0.997817094454925,
        0.997812305924841,
        0.9978070667828608,
        0.9978013106122325,
        0.9977949573488758,
        0.9979622411430684,
        0.9982239456097534,
        0.9984901538115333,
        0.9987605994098896,
        0.9990349853294376,
        0.9995177442719444,
        1.0001477447359568,
        1.0007896336142619,
        1.001443420477501,
        1.0021093091820772,
        1.0027878049903634,
        1.0034798491972945,
        1.0041869471264913,
        1.0049111470842644,
        1.0056543943325655,
        1.006415818683618,
        1.0071828641350455,
        1.007904327181489,
        1.0083908590088804,
    ]
    x_range = np.arange(0, 1, 0.01)

    fig, ax = plt.subplots()
    ax.axhline(y=1, color="grey", ls="solid", lw=1)
    ax.plot(x_range, ps_data_kill_zero, label="ps", ls="solid", lw=3)
    ax.plot(x_range, pc_data_kill_zero, label="pc", ls="dashdot", lw=3)
    ax.plot(x_range, pa_data_kill_zero, label="pa", ls="dotted", lw=3)
    ax.set_title("Kill and Zero")
    ax.set_xlabel("px")
    ax.set_ylabel("rho")
    ax.legend()
    plt.show()

    # Kill and Hold plot
    ps_data_kill_hold = [
        0.9978984860292592,
        0.9978984862817318,
        0.9978984865393534,
        0.9978984868022858,
        0.9978984870707013,
        0.9978984873447672,
        0.9978984876246627,
        0.9978984879105776,
        0.9978984882027102,
        0.9978984885012605,
        0.9978984888064465,
        0.9978984891184925,
        0.9978984894376304,
        0.9978984897641039,
        0.9978984900981687,
        0.9978984904400983,
        0.997898490790167,
        0.9978984911486719,
        0.9978984915159202,
        0.9978984918922374,
        0.9978984922779635,
        0.9978984926734559,
        0.9978984930790898,
        0.9978984934952583,
        0.9978984939223797,
        0.9978984943608907,
        0.9978984948112563,
        0.9978984952739571,
        0.9978984957495161,
        0.9978984962384689,
        0.9978984967413932,
        0.9978984972588949,
        0.9978984977916199,
        0.9978984983402501,
        0.9978984989055008,
        0.9978984994881483,
        0.9978985000890029,
        0.9978985007089362,
        0.997898501348865,
        0.9978985020097788,
        0.9978985026927241,
        0.9978985033988178,
        0.9978985041292661,
        0.9978985048853428,
        0.9978985056684271,
        0.997898506479988,
        0.9978985073216065,
        0.9978985081949873,
        0.9978985091019632,
        0.9978985100445085,
        0.9978985110247592,
        0.9978985120450219,
        0.997898513107799,
        0.997898514215805,
        0.9978985153719862,
        0.9978985165795626,
        0.9978985178420263,
        0.9978985191632185,
        0.9978985205473302,
        0.9978985219989677,
        0.9978985235231876,
        0.9978985251255823,
        0.9978985268123244,
        0.9978985285902459,
        0.9978985304669554,
        0.9978985324509151,
        0.9978985345515892,
        0.9978985367795916,
        0.9978985391468598,
        0.997898541666876,
        0.9978985443549092,
        0.9978985472283517,
        0.9978985503070611,
        0.9978985536138556,
        0.9978985571750534,
        0.9978985610211909,
        0.9978985651878864,
        0.9978985697169624,
        0.9978985746578349,
        0.9978985800693504,
        0.9978985860221151,
        0.9978985926016063,
        0.9986281596844219,
        1.005814579163735,
        1.0131157921056069,
        1.0203442696626326,
        1.0274517936122698,
        1.0344084590943294,
        1.0411871515029416,
        1.0477579183109071,
        1.0540846614018,
        1.0601218552238083,
        1.0658100856500947,
        1.071069080399318,
        1.075785880940787,
        1.0797931012490305,
        1.082824812325663,
        1.084413875174669,
        1.0835969881279695,
        1.0776664649891043,
    ]
    pc_data_kill_hold = [
        0.9978984860292592,
        0.9979126112653465,
        0.9979271037089629,
        0.9979419483312584,
        0.9979571307108627,
        0.9979726370136309,
        0.997988453972389,
        0.9980045688667076,
        0.9980209695029331,
        0.9980376441944303,
        0.9980545817421955,
        0.9980717714158958,
        0.9980892029352973,
        0.9981068664522256,
        0.9981247525330199,
        0.9981428521414988,
        0.9981611566224986,
        0.9981796576859516,
        0.9981983473914939,
        0.9982172181336756,
        0.9982362626276661,
        0.9982554738955516,
        0.9982748452531268,
        0.9982943702972323,
        0.9983140428935999,
        0.9983338571651906,
        0.9983538074810219,
        0.9983738884454492,
        0.998394094887934,
        0.9984144218532021,
        0.9984348645918716,
        0.9984554185514615,
        0.998476079367783,
        0.9984968428567441,
        0.9985177050064711,
        0.9985386619698055,
        0.9985597100571175,
        0.9985808457294477,
        0.9986020655919392,
        0.998623366387581,
        0.9986447449911948,
        0.9986661984037235,
        0.9986877237467502,
        0.9987093182572621,
        0.9987309792826533,
        0.9987527042759343,
        0.9987744907911659,
        0.9987963364790733,
        0.9988182390828777,
        0.9988401964342761,
        0.9988622064496255,
        0.9988842671262667,
        0.9989063765390249,
        0.9989285328368434,
        0.9989507342395604,
        0.9989729790348408,
        0.9989952655752121,
        0.99901759227523,
        0.9990399576087657,
        0.9990623601064045,
        0.9990847983529437,
        0.9991072709849851,
        0.999129776688639,
        0.9991523141973033,
        0.9991748822895423,
        0.9991974797870288,
        0.9992201055525811,
        0.9992427584882694,
        0.9992654375335726,
        0.9992881416636329,
        0.9993108698875546,
        0.9993336212467593,
        0.9993563948134025,
        0.9993791896888545,
        0.9994195459291113,
        0.999558409451343,
        0.9996978344852497,
        0.9998379059448115,
        1.0000297885536367,
        1.0003137036164256,
        1.0006019528710535,
        1.0008997193960245,
        1.0012535378489382,
        1.0055260783243236,
        1.01290130355763,
        1.0201938457881885,
        1.0273562563071506,
        1.0343666442587687,
        1.0412023091764322,
        1.0478363258551944,
        1.054235386532086,
        1.0603571464833703,
        1.066146296428981,
        1.0715282924566574,
        1.0763986895539588,
        1.0806035957527016,
        1.083900191546168,
        1.0858652561517894,
        1.0856330647647126,
        1.0807823307315607,
    ]
    pa_data_kill_hold = [
        0.9978984860292592,
        0.9978984862817281,
        0.9978984865393543,
        0.9978984868022875,
        0.997898487070702,
        0.9978984873447659,
        0.9978984876246634,
        0.997898487910578,
        0.9978984882027095,
        0.9978984885012607,
        0.997898488806446,
        0.9978984891184937,
        0.9978984894376299,
        0.997898489764103,
        0.99789849009817,
        0.9978984904400998,
        0.9978984907901691,
        0.9978984911486708,
        0.9978984915159195,
        0.9978984918922366,
        0.9978984922779631,
        0.9978984926734554,
        0.9978984930790854,
        0.9978984934952563,
        0.9978984939223793,
        0.9978984943608911,
        0.9978984948112544,
        0.9978984952739576,
        0.9978984957495157,
        0.9978984962384672,
        0.9978984967413924,
        0.9978984972588961,
        0.9978984977916201,
        0.9978984983402501,
        0.9978984989054998,
        0.9978984994881481,
        0.9978985000890045,
        0.9978985007089344,
        0.9978985013488667,
        0.9978985020097789,
        0.9978985026927234,
        0.9978985033988196,
        0.9978985041292661,
        0.9978985048853468,
        0.9978985056684264,
        0.9978985064799872,
        0.9978985073216076,
        0.9978985081949879,
        0.9978985091019636,
        0.9978985100445074,
        0.9978985110247587,
        0.9978985120450216,
        0.9978985131077971,
        0.9978985142158028,
        0.9978985153719866,
        0.9978985165795595,
        0.9978985178420279,
        0.9978985191632204,
        0.9978985205473282,
        0.9978985219989642,
        0.9978985235231874,
        0.9978985251255816,
        0.9978985268123234,
        0.9978985285902467,
        0.997898530466956,
        0.9978985324509142,
        0.9978985345515892,
        0.9978985367795932,
        0.9978985391468606,
        0.9978985416668759,
        0.9978985443549087,
        0.9978985472283487,
        0.9978985503070598,
        0.9978985536138554,
        0.9978985571750544,
        0.9978985610211893,
        0.9978985651878866,
        0.9978985697169596,
        0.9978985746578358,
        0.9978985800693498,
        0.997898586022116,
        0.9978985926016035,
        0.9984542080845076,
        1.0059833293452622,
        1.0134029079422973,
        1.0206985134834754,
        1.0278540499268765,
        1.034850595395227,
        1.0416653459437988,
        1.0482702865046438,
        1.0546303278690317,
        1.060700554010665,
        1.066421973991321,
        1.0717146467594005,
        1.076465895459925,
        1.0805085718925576,
        1.0835768817251614,
        1.0852034425335202,
        1.0844230589562682,
        1.0785159431192144,
    ]
    x_range = np.arange(0, 1, 0.01)

    fig, ax = plt.subplots()
    ax.axhline(y=1, color="grey", ls="solid", lw=1)
    ax.plot(x_range, ps_data_kill_hold, label="ps", ls="solid", lw=3)
    ax.plot(x_range, pc_data_kill_hold, label="pc", ls="dashdot", lw=3)
    ax.plot(x_range, pa_data_kill_hold, label="pa", ls="dotted", lw=3)
    ax.set_title("Kill and Hold")
    ax.set_xlabel("px")
    ax.set_ylabel("rho")
    ax.legend()
    plt.show()

    # Skip and Zero plot
    ps_data_skip_zero = [
        0.9978984860292592,
        0.9978984862817318,
        0.9978984865393534,
        0.9978984868022858,
        0.9978984870707013,
        0.9978984873447672,
        0.9978984876246627,
        0.9978984879105776,
        0.9978984882027102,
        0.9978984885012605,
        0.9978984888064465,
        0.9978984891184925,
        0.9978984894376304,
        0.9978984897641039,
        0.9978984900981687,
        0.9978984904400983,
        0.997898490790167,
        0.9978984911486719,
        0.9978984915159202,
        0.9978984918922374,
        0.9978984922779635,
        0.9978984926734559,
        0.9978984930790898,
        0.9978984934952583,
        0.9978984939223797,
        0.9978984943608907,
        0.9978984948112563,
        0.9978984952739571,
        0.9978984957495161,
        0.9978984962384689,
        0.9978984967413932,
        0.9978984972588949,
        0.9978984977916199,
        0.9978984983402501,
        0.9978984989055008,
        0.9978984994881483,
        0.9978985000890029,
        0.9978985007089362,
        0.997898501348865,
        0.9978985020097788,
        0.9978985026927241,
        0.9978985033988178,
        0.9978985041292661,
        0.9978985048853428,
        0.9978985056684271,
        0.997898506479988,
        0.9978985073216065,
        0.9978985081949873,
        0.9978985091019632,
        0.9978985100445085,
        0.9978985110247592,
        0.9978985120450219,
        0.997898513107799,
        0.997898514215805,
        0.9978985153719862,
        0.9978985165795626,
        0.9978985178420263,
        0.9978985191632185,
        0.9978985205473302,
        0.9978985219989677,
        0.9978985235231876,
        0.9978985251255823,
        0.9978985268123244,
        0.9978985285902459,
        0.9978985304669554,
        0.9978985324509151,
        0.9978985345515892,
        0.9978985367795916,
        0.9978985391468598,
        0.997898541666876,
        0.9978985443549092,
        0.9978985472283517,
        0.9978985503070611,
        0.9978985536138556,
        0.9978985571750534,
        0.9978985610211909,
        0.9978985651878864,
        0.9978985697169624,
        0.9978985746578349,
        0.9978985800693504,
        0.9978985860221151,
        0.9978985926016063,
        0.9986281596844219,
        1.005814579163735,
        1.0131157921056069,
        1.0203442696626326,
        1.0274517936122698,
        1.0344084590943294,
        1.0411871515029416,
        1.0477579183109071,
        1.0540846614018,
        1.0601218552238083,
        1.0658100856500947,
        1.071069080399318,
        1.075785880940787,
        1.0797931012490305,
        1.082824812325663,
        1.084413875174669,
        1.0835969881279695,
        1.0776664649891043,
    ]
    pc_data_skip_zero = [
        0.9978984860292592,
        0.9979123707853905,
        0.9979266408240767,
        0.9979412803513606,
        0.9979562741882387,
        0.9979716077532703,
        0.997987267044712,
        0.9980032386223362,
        0.9980195095890375,
        0.9980360675724222,
        0.998052900706441,
        0.9980699976131984,
        0.9980873473849512,
        0.9981049395664361,
        0.9981227641375471,
        0.998140811496372,
        0.9981590724426761,
        0.9981775381618314,
        0.9981962002092133,
        0.9982150504950804,
        0.9982340812699381,
        0.9982532851104169,
        0.9982726549056097,
        0.9982921838439575,
        0.9983118654005607,
        0.9983316933250176,
        0.9983516616297293,
        0.9983717645786339,
        0.9983919966764446,
        0.9984123526582772,
        0.9984328274797462,
        0.9984534163074273,
        0.9984741145097762,
        0.9984949176483799,
        0.9985158214696168,
        0.998536821896645,
        0.9985579150217793,
        0.9985790970991412,
        0.9986003645376806,
        0.9986217138944706,
        0.9986431418682924,
        0.9986646452935367,
        0.9986862211343182,
        0.9987078664789077,
        0.9987295785343396,
        0.9987513546213204,
        0.9987731921693213,
        0.9987950887118971,
        0.9988170418822022,
        0.9988390494087129,
        0.99886110911112,
        0.9989744341973246,
        0.9991955895508934,
        0.9994187415686175,
        0.9996439435707286,
        0.9998825945367704,
        1.0003449935613404,
        1.000812248861758,
        1.001284489110021,
        1.0017618441017602,
        1.0022444423534438,
        1.0027324092901724,
        1.0032258655424604,
        1.003724925146868,
        1.0042296935359374,
        1.0047402652342363,
        1.0052567211857466,
        1.005779125636134,
        1.0063075224852849,
        1.0068419310122592,
        1.0073823408566687,
        1.0079287061164504,
        1.0084809383914763,
        1.0090388985626693,
        1.0096023870451645,
        1.0101711321871025,
        1.0107447763979778,
        1.0113228594728714,
        1.0119047984213811,
        1.0124898628949852,
        1.0130771450091762,
        1.0136655219408806,
        1.0142536090899994,
        1.0148397007390253,
        1.0154216938872758,
        1.015996989049489,
        1.0165623589144404,
        1.0171137712105802,
        1.0176461447725598,
        1.0181530055358503,
        1.0186259879587638,
        1.0190540890459523,
        1.0194225093936136,
        1.0197107690159848,
        1.0198894674933248,
        1.0199143006024287,
        1.0197139119682963,
        1.0191617142908933,
        1.017995663323188,
        1.015485675838009,
    ]
    pa_data_skip_zero = [
        0.9978984860292592,
        0.9978982337083446,
        0.9978979761880671,
        0.9978977133060668,
        0.9978974448931709,
        0.9978971707730036,
        0.9978968907616139,
        0.9978966046670679,
        0.9978963122889885,
        0.9978960134181214,
        0.997895707835802,
        0.9978953953134525,
        0.9978950756119886,
        0.9978947484812202,
        0.997894413659195,
        0.997894070871516,
        0.9978937198305657,
        0.9978933602347186,
        0.9978929917674745,
        0.9978926140965342,
        0.9978922268727923,
        0.9978918297292716,
        0.9978914222799463,
        0.9978910041185264,
        0.9978905748170666,
        0.9978901339245434,
        0.9978896809652443,
        0.9978892154370843,
        0.9978887368097438,
        0.9978882445226441,
        0.99788773798278,
        0.9978872165623165,
        0.9978866795960197,
        0.997886126378423,
        0.9978855561607295,
        0.9978849681474398,
        0.9978843614926691,
        0.9978837352960728,
        0.997883088598421,
        0.9978824203766744,
        0.9978817295386222,
        0.9978810149169189,
        0.9978802752625244,
        0.9978795092374247,
        0.9978787154065868,
        0.9978778922289826,
        0.9978770380476619,
        0.9978761510786117,
        0.9978752293983723,
        0.9978742709301459,
        0.9978732734282134,
        0.9978722344604253,
        0.9978711513884513,
        0.9978700213454871,
        0.9978688412109997,
        0.997867607582047,
        0.9978663167406195,
        0.9978649646163605,
        0.9978635467438584,
        0.9978620582135854,
        0.9978604936153551,
        0.9978588469728988,
        0.9978571116679721,
        0.9978552803518939,
        0.9978533448420802,
        0.9978512960005177,
        0.9978491235903731,
        0.9978468161060401,
        0.9978443605707171,
        0.9978417422940145,
        0.9978389445801669,
        0.9978359483746516,
        0.9978327318335983,
        0.9978292697955998,
        0.9978255331292064,
        0.9978214879207145,
        0.997817094454925,
        0.997812305924841,
        0.9978070667828608,
        0.9978013106122325,
        0.9977949573488758,
        0.9979622411430684,
        0.9982239456097534,
        0.9984901538115333,
        0.9987605994098896,
        0.9990349853294376,
        0.9995177442719444,
        1.0001477447359568,
        1.0007896336142619,
        1.001443420477501,
        1.0021093091820772,
        1.0027878049903634,
        1.0034798491972945,
        1.0041869471264913,
        1.0049111470842644,
        1.0056543943325655,
        1.006415818683618,
        1.0071828641350455,
        1.007904327181489,
        1.0083908590088804,
    ]
    x_range = np.arange(0, 1, 0.01)

    fig, ax = plt.subplots()
    ax.axhline(y=1, color="grey", ls="solid", lw=1)
    ax.plot(x_range, ps_data_skip_zero, label="ps", ls="solid", lw=3)
    ax.plot(x_range, pc_data_skip_zero, label="pc", ls="dashdot", lw=3)
    ax.plot(x_range, pa_data_skip_zero, label="pa", ls="dotted", lw=3)
    ax.set_title("Skip and Zero")
    ax.set_xlabel("px")
    ax.set_ylabel("rho")
    ax.legend()
    plt.show()

    # Skip and Hold plot
    ps_data_skip_hold = [
        0.9978984860292592,
        0.9978984862817318,
        0.9978984865393534,
        0.9978984868022858,
        0.9978984870707013,
        0.9978984873447672,
        0.9978984876246627,
        0.9978984879105776,
        0.9978984882027102,
        0.9978984885012605,
        0.9978984888064465,
        0.9978984891184925,
        0.9978984894376304,
        0.9978984897641039,
        0.9978984900981687,
        0.9978984904400983,
        0.997898490790167,
        0.9978984911486719,
        0.9978984915159202,
        0.9978984918922374,
        0.9978984922779635,
        0.9978984926734559,
        0.9978984930790898,
        0.9978984934952583,
        0.9978984939223797,
        0.9978984943608907,
        0.9978984948112563,
        0.9978984952739571,
        0.9978984957495161,
        0.9978984962384689,
        0.9978984967413932,
        0.9978984972588949,
        0.9978984977916199,
        0.9978984983402501,
        0.9978984989055008,
        0.9978984994881483,
        0.9978985000890029,
        0.9978985007089362,
        0.997898501348865,
        0.9978985020097788,
        0.9978985026927241,
        0.9978985033988178,
        0.9978985041292661,
        0.9978985048853428,
        0.9978985056684271,
        0.997898506479988,
        0.9978985073216065,
        0.9978985081949873,
        0.9978985091019632,
        0.9978985100445085,
        0.9978985110247592,
        0.9978985120450219,
        0.997898513107799,
        0.997898514215805,
        0.9978985153719862,
        0.9978985165795626,
        0.9978985178420263,
        0.9978985191632185,
        0.9978985205473302,
        0.9978985219989677,
        0.9978985235231876,
        0.9978985251255823,
        0.9978985268123244,
        0.9978985285902459,
        0.9978985304669554,
        0.9978985324509151,
        0.9978985345515892,
        0.9978985367795916,
        0.9978985391468598,
        0.997898541666876,
        0.9978985443549092,
        0.9978985472283517,
        0.9978985503070611,
        0.9978985536138556,
        0.9978985571750534,
        0.9978985610211909,
        0.9978985651878864,
        0.9978985697169624,
        0.9978985746578349,
        0.9978985800693504,
        0.9978985860221151,
        0.9978985926016063,
        0.9986281596844219,
        1.005814579163735,
        1.0131157921056069,
        1.0203442696626326,
        1.0274517936122698,
        1.0344084590943294,
        1.0411871515029416,
        1.0477579183109071,
        1.0540846614018,
        1.0601218552238083,
        1.0658100856500947,
        1.071069080399318,
        1.075785880940787,
        1.0797931012490305,
        1.082824812325663,
        1.084413875174669,
        1.0835969881279695,
        1.0776664649891043,
    ]
    pc_data_skip_hold = [
        0.9978984860292592,
        0.9979126115218468,
        0.9979271042313941,
        0.9979419491241205,
        0.9979571317744051,
        0.9979726383445007,
        0.9979884555641768,
        0.9980045707104847,
        0.9980209715876632,
        0.9980376465074052,
        0.9980545842693835,
        0.9980717741422382,
        0.9980892058450084,
        0.9981068695290358,
        0.9981247557603622,
        0.9981428555027265,
        0.9981611601010255,
        0.9981796612653923,
        0.9981983510557861,
        0.998217221867168,
        0.9982362664152152,
        0.9982554777225756,
        0.9982748491056656,
        0.9982943741619974,
        0.9983140467579921,
        0.9983338610173437,
        0.9983538113097974,
        0.9983738922404649,
        0.9983940986395488,
        0.9984144255525333,
        0.9984348682307681,
        0.9984554221225029,
        0.9984760828642674,
        0.9984968462726644,
        0.9985177083364944,
        0.9985386652092609,
        0.998559713201961,
        0.9985808487762444,
        0.9986020685378404,
        0.9986233692302806,
        0.9986447477289206,
        0.998666201035204,
        0.9986877262711772,
        0.9987093206742803,
        0.9987309815923153,
        0.9987527064786862,
        0.9987744928878082,
        0.9987963384707503,
        0.9988182409710221,
        0.9988401982206223,
        0.9988622081361554,
        0.9988842687151949,
        0.9989063780327676,
        0.9989285342380082,
        0.9989507355509193,
        0.9989729802593046,
        0.9989952667158112,
        0.999017593335095,
        0.9990399585911129,
        0.9990623610145111,
        0.9990847991901302,
        0.9991072717546043,
        0.9991297773940584,
        0.999152314841895,
        0.9991748828766553,
        0.9991974803199899,
        0.9992201060346738,
        0.9992427589227236,
        0.9992654379235635,
        0.9992881420122586,
        0.9993108701978342,
        0.9993336215216226,
        0.9993563950556846,
        1.0030120094898642,
        1.0085730257556746,
        1.0140122917890182,
        1.0193125297182797,
        1.0244657048675891,
        1.0294644973272078,
        1.0343012206160604,
        1.0389674846504016,
        1.0434539914840888,
        1.0477503465648643,
        1.0518448484693061,
        1.0557242365608521,
        1.0593733773232914,
        1.0627748653197915,
        1.065908504819468,
        1.0687506210460263,
        1.0712731204955,
        1.0734421667713943,
        1.0752162380021655,
        1.0765431298680785,
        1.0773550336296713,
        1.0775598135095878,
        1.07702409023183,
        1.07553679982642,
        1.0727200693103625,
        1.0677684052241139,
        1.058370714682521,
    ]
    pa_data_skip_hold = [
        0.9978984860292592,
        0.9978984862817281,
        0.9978984865393543,
        0.9978984868022875,
        0.997898487070702,
        0.9978984873447659,
        0.9978984876246634,
        0.997898487910578,
        0.9978984882027095,
        0.9978984885012607,
        0.997898488806446,
        0.9978984891184937,
        0.9978984894376299,
        0.997898489764103,
        0.99789849009817,
        0.9978984904400998,
        0.9978984907901691,
        0.9978984911486708,
        0.9978984915159195,
        0.9978984918922366,
        0.9978984922779631,
        0.9978984926734554,
        0.9978984930790854,
        0.9978984934952563,
        0.9978984939223793,
        0.9978984943608911,
        0.9978984948112544,
        0.9978984952739576,
        0.9978984957495157,
        0.9978984962384672,
        0.9978984967413924,
        0.9978984972588961,
        0.9978984977916201,
        0.9978984983402501,
        0.9978984989054998,
        0.9978984994881481,
        0.9978985000890045,
        0.9978985007089344,
        0.9978985013488667,
        0.9978985020097789,
        0.9978985026927234,
        0.9978985033988196,
        0.9978985041292661,
        0.9978985048853468,
        0.9978985056684264,
        0.9978985064799872,
        0.9978985073216076,
        0.9978985081949879,
        0.9978985091019636,
        0.9978985100445074,
        0.9978985110247587,
        0.9978985120450216,
        0.9978985131077971,
        0.9978985142158028,
        0.9978985153719866,
        0.9978985165795595,
        0.9978985178420279,
        0.9978985191632204,
        0.9978985205473282,
        0.9978985219989642,
        0.9978985235231874,
        0.9978985251255816,
        0.9978985268123234,
        0.9978985285902467,
        0.997898530466956,
        0.9978985324509142,
        0.9978985345515892,
        0.9978985367795932,
        0.9978985391468606,
        0.9978985416668759,
        0.9978985443549087,
        0.9978985472283487,
        0.9978985503070598,
        0.9978985536138554,
        0.9978985571750544,
        0.9978985610211893,
        0.9978985651878866,
        0.9978985697169596,
        0.9978985746578358,
        0.9978985800693498,
        0.997898586022116,
        0.9978985926016035,
        0.9984542080845076,
        1.0059833293452622,
        1.0134029079422973,
        1.0206985134834754,
        1.0278540499268765,
        1.034850595395227,
        1.0416653459437988,
        1.0482702865046438,
        1.0546303278690317,
        1.060700554010665,
        1.066421973991321,
        1.0717146467594005,
        1.076465895459925,
        1.0805085718925576,
        1.0835768817251614,
        1.0852034425335202,
        1.0844230589562682,
        1.0785159431192144,
    ]
    x_range = np.arange(0, 1, 0.01)

    fig, ax = plt.subplots()
    ax.axhline(y=1, color="grey", ls="solid", lw=1)
    ax.plot(x_range, ps_data_skip_hold, label="ps", ls="solid", lw=3)
    ax.plot(x_range, pc_data_skip_hold, label="pc", ls="dashdot", lw=3)
    ax.plot(x_range, pa_data_skip_hold, label="pa", ls="dotted", lw=3)
    ax.set_title("Skip and Hold")
    ax.set_xlabel("px")
    ax.set_ylabel("rho")
    ax.legend()
    plt.show()


def print_table2():
    print(f"Kill+Zero: {get_rho('kill_zero', ps=0.15, pc=0.4, pa=0.05)}")
    print(f"Kill+Hold: {get_rho('kill_hold', ps=0.15, pc=0.4, pa=0.05)}")
    print(f"Skip+Zero: {get_rho('skip_zero', ps=0.15, pc=0.4, pa=0.05)}")
    print(f"Skip+Hold: {get_rho('skip_zero', ps=0.15, pc=0.4, pa=0.05)}")


if __name__ == "__main__":
    # compute_single_variations("skip_hold")
    # compute_double_variations("skip_hold")
    # plot_fig6()
    print_table2()
