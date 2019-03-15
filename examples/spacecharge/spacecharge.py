from pyoptics import madlang,optics
import pyoptics.tfsdata as tfs
import pysixtrack
import pysixtrack.helpers as hp 
import numpy as np

#see sps/madx/a001_track_thin.madx
mad=madlang.open('madx/SPS_Q20_thin.seq')
mad.acta_31637.volt=4.5
mad.acta_31637.lag=0.5


elems,rest,iconv=mad.sps.expand_struct(pysixtrack.element_types)

pbench=optics.open('madx/track.obs0001.p0001')
sps=pysixtrack.Line(elements= [e[2] for e in elems])
spstwiss=tfs.open('madx/twiss_SPS_Q20_thin.tfs')

gamma = spstwiss['param']['gamma']
beta = np.sqrt(1.-1./gamma**2)
betagamma = beta*gamma



for k in spstwiss:
    try:
        spstwiss[k] = spstwiss[k][1:-1]
    except TypeError:
        pass
assert (len(spstwiss['s']) == len(elems))


s_lastSCkick = 0
s_SCkicks = [0]
min_distance = 6.
new_element_list = []
line_density = 1
epsn_x = 2e-6
epsn_y = 2e-6
dpp_rms = 1.5e-3
SC_elements_list = []
for i, e in enumerate(elems):
    s = spstwiss['s'][i]
    new_element_list.append(e)
    if s-s_lastSCkick > min_distance or i==(len(elems)-1):
        beta_x = spstwiss['betx'][i]
        beta_y = spstwiss['bety'][i]
        d_x = spstwiss['dx'][i]*beta
        d_y = spstwiss['dy'][i]*beta
        newSC = ('SC%i'%(len(SC_elements_list)), 'SpaceChargeCoast', 
            pysixtrack.SpaceChargeCoast(
            line_density=line_density,
            sigma_x=np.sqrt(beta_x*epsn_x/betagamma + d_x**2*dpp_rms**2),
            sigma_y=np.sqrt(beta_y*epsn_y/betagamma + d_y**2*dpp_rms**2),
            length=s-s_lastSCkick,
            min_sigma_diff=1e-10,
            Delta_x=spstwiss['x'][i],
            Delta_y=spstwiss['x'][i],
            enabled=True))
        new_element_list.append(newSC)
        SC_elements_list.append(newSC)
        s_SCkicks.append(s)
        s_lastSCkick = s

# to verify that integrated length of SC kicks corresponds to circumference
print(sum([sc[2].length for sc in SC_elements_list]))




p0c_eV=25.92
n_part = 10
zeros = np.zeros(n_part)
p=pysixtrack.Particles(x=np.linspace(0.,0.01,n_part),px=zeros,y=zeros,py=zeros,tau=zeros,pt=zeros)
ring = hp.Ring(new_element_list, p0c=p0c_eV)

print('start tracking')
for t in range(1000):
    print('turn: %03d'%t)
    ring.track(p)


# spstwiss['s'] 
# print(len(iconv), len(spstwiss['s']))

'''
def get_part(pbench,ii):
    pstart=[pbench[n][ii] for n in 'x px y py t pt'.split()]
    pstart=dict(zip('x px y py tau ptau'.split(),pstart))
    prun=pysixtrack.Particles(energy0=pbench.e[ii]*1e9,**pstart)
    return prun

def compare(prun,pbench):
    out=[]
    for att in 'x px y py tau ptau'.split():
        vrun=getattr(prun,att)
        vbench=getattr(pbench,att)
        diff=vrun-vbench
        out.append(abs(diff))
        print(f"{att:<5} {vrun:22.13e} {vbench:22.13e} {diff:22.13g}")
    print(f"max {max(out):21.12e}")
    return max(out)

prun=get_part(pbench,0)
for turn in range(1,30):
    sps.track(prun)
    compare(prun,get_part(pbench,turn))




'''