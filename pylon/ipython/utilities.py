import matplotlib.pyplot as plt
import json
import requests
import time
import pandas as pd
import datetime
from datasift import Client
import os


client = None


DASH_OVERVIEW = [[('timeSeries','hour',1,'Time Series'),('freqDist','fb.type',4,'Interaction Types')],
                 [('freqDist','fb.author.type',4, 'Story authors'),('freqDist','fb.parent.author.type',4, 'Engagement authors')],
                 [('freqDist','fb.parent.author.region',4,'Engagement Regions'),('freqDist','fb.parent.author.age',4, 'Engagement Ages')],
                [('freqDist','fb.parent.topics.category',4, 'Topic Categories'),('freqDist','fb.parent.topics.name',4,'Topics')]]

SPAM_TAGS = '''tag "profanity" {
  fb.content any "4r5e,5h1t,5hit,a55,anal,anus,ar5e,arrse,arse,ass,ass-fucker,asses,assfucker,assfukka,asshole,assholes,asswhole,a_s_s,b!tch,b00bs,b17ch,b1tch,ballbag,balls,ballsack,bastard,beastial,beastiality,bellend,bestial,bestiality,bi+ch,biatch,bitch,bitcher,bitchers,bitches,bitchin,bitching,bloody,blow job,blowjob,blowjobs,boiolas,bollock,bollok,boner,boob,boobs,booobs,boooobs,booooobs,booooooobs,breasts,buceta,bugger,bum,bunny fucker,butt,butthole,buttmuch,buttplug,c0ck,c0cksucker,carpet muncher,cawk,chink,cipa,cl1t,clit,clitoris,clits,cnut,cock,cock-sucker,cockface,cockhead,cockmunch,cockmuncher,cocks,cocksuck ,cocksucked ,cocksucker,cocksucking,cocksucks ,cocksuka,cocksukka,cok,cokmuncher,coksucka,coon,cox,crap,cum,cummer,cumming,cums,cumshot,cunilingus,cunillingus,cunnilingus,cunt,cuntlick ,cuntlicker ,cuntlicking ,cunts,cyalis,cyberfuc,cyberfuck ,cyberfucked ,cyberfucker,cyberfuckers,cyberfucking ,d1ck,damn,dick,dickhead,dildo,dildos,dink,dinks,dirsa,dlck,dog-fucker,doggin,dogging,donkeyribber,doosh,duche,dyke,ejaculate,ejaculated,ejaculates ,ejaculating ,ejaculatings,ejaculation,ejakulate,f u c k,f u c k e r,f4nny,fag,fagging,faggitt,faggot,faggs,fagot,fagots,fags,fanny,fannyflaps,fannyfucker,fanyy,fatass,fcuk,fcuker,fcuking,feck,fecker,felching,fellate,fellatio,fingerfuck ,fingerfucked ,fingerfucker ,fingerfuckers,fingerfucking ,fingerfucks ,fistfuck,fistfucked ,fistfucker ,fistfuckers ,fistfucking ,fistfuckings ,fistfucks ,flange,fook,fooker,fuck,fucka,fucked,fucker,fuckers,fuckhead,fuckheads,fuckin,fucking,fuckings,fuckingshitmotherfucker,fuckme ,fucks,fuckwhit,fuckwit,fudge packer,fudgepacker,fuk,fuker,fukker,fukkin,fuks,fukwhit,fukwit,fux,fux0r,f_u_c_k,gangbang,gangbanged ,gangbangs ,gaylord,gaysex,goatse,God,god-dam,god-damned,goddamn,goddamned,hardcoresex ,hell,heshe,hoar,hoare,hoer,homo,hore,horniest,horny,hotsex,jack-off ,jackoff,jap,jerk-off ,jism,jiz ,jizm ,jizz,kawk,knob,knobead,knobed,knobend,knobhead,knobjocky,knobjokey,kock,kondum,kondums,kum,kummer,kumming,kums,kunilingus,l3i+ch,l3itch,labia,lmfao,lust,lusting,m0f0,m0fo,m45terbate,ma5terb8,ma5terbate,masochist,master-bate,masterb8,masterbat*,masterbat3,masterbate,masterbation,masterbations,masturbate,mo-fo,mof0,mofo,mothafuck,mothafucka,mothafuckas,mothafuckaz,mothafucked ,mothafucker,mothafuckers,mothafuckin,mothafucking ,mothafuckings,mothafucks,mother fucker,motherfuck,motherfucked,motherfucker,motherfuckers,motherfuckin,motherfucking,motherfuckings,motherfuckka,motherfucks,muff,mutha,muthafecker,muthafuckker,muther,mutherfucker,n1gga,n1gger,nazi,nigg3r,nigg4h,nigga,niggah,niggas,niggaz,nigger,niggers ,nob,nob jokey,nobhead,nobjocky,nobjokey,numbnuts,nutsack,orgasim ,orgasims ,orgasm,orgasms ,p0rn,pawn,pecker,penis,penisfucker,phonesex,phuck,phuk,phuked,phuking,phukked,phukking,phuks,phuq,pigfucker,pimpis,piss,pissed,pisser,pissers,pisses ,pissflaps,pissin ,pissing,pissoff ,poop,porn,porno,pornography,pornos,prick,pricks ,pron,pube,pusse,pussi,pussies,pussy,pussys ,rectum,retard,rimjaw,rimming,s hit,s.o.b.,sadist,schlong,screwing,scroat,scrote,scrotum,semen,sex,sh!+,sh!t,sh1t,shag,shagger,shaggin,shagging,shemale,shi+,shit,shitdick,shite,shited,shitey,shitfuck,shitfull,shithead,shiting,shitings,shits,shitted,shitter,shitters ,shitting,shittings,shitty ,skank,slut,sluts,smegma,smut,snatch,son-of-a-bitch,spac,spunk,s_h_i_t,t1tt1e5,t1tties,teets,teez,testical,testicle,tit,titfuck,tits,titt,tittie5,tittiefucker,titties,tittyfuck,tittywank,titwank,tosser,turd,tw4t,twat,twathead,twatty,twunt,twunter,v14gra,v1gra,vagina,viagra,vulva,w00se,wang,wank,wanker,wanky,whoar,whore,willies,willy,xrated,xxx" or
  fb.parent.content any "4r5e,5h1t,5hit,a55,anal,anus,ar5e,arrse,arse,ass,ass-fucker,asses,assfucker,assfukka,asshole,assholes,asswhole,a_s_s,b!tch,b00bs,b17ch,b1tch,ballbag,balls,ballsack,bastard,beastial,beastiality,bellend,bestial,bestiality,bi+ch,biatch,bitch,bitcher,bitchers,bitches,bitchin,bitching,bloody,blow job,blowjob,blowjobs,boiolas,bollock,bollok,boner,boob,boobs,booobs,boooobs,booooobs,booooooobs,breasts,buceta,bugger,bum,bunny fucker,butt,butthole,buttmuch,buttplug,c0ck,c0cksucker,carpet muncher,cawk,chink,cipa,cl1t,clit,clitoris,clits,cnut,cock,cock-sucker,cockface,cockhead,cockmunch,cockmuncher,cocks,cocksuck ,cocksucked ,cocksucker,cocksucking,cocksucks ,cocksuka,cocksukka,cok,cokmuncher,coksucka,coon,cox,crap,cum,cummer,cumming,cums,cumshot,cunilingus,cunillingus,cunnilingus,cunt,cuntlick ,cuntlicker ,cuntlicking ,cunts,cyalis,cyberfuc,cyberfuck ,cyberfucked ,cyberfucker,cyberfuckers,cyberfucking ,d1ck,damn,dick,dickhead,dildo,dildos,dink,dinks,dirsa,dlck,dog-fucker,doggin,dogging,donkeyribber,doosh,duche,dyke,ejaculate,ejaculated,ejaculates ,ejaculating ,ejaculatings,ejaculation,ejakulate,f u c k,f u c k e r,f4nny,fag,fagging,faggitt,faggot,faggs,fagot,fagots,fags,fanny,fannyflaps,fannyfucker,fanyy,fatass,fcuk,fcuker,fcuking,feck,fecker,felching,fellate,fellatio,fingerfuck ,fingerfucked ,fingerfucker ,fingerfuckers,fingerfucking ,fingerfucks ,fistfuck,fistfucked ,fistfucker ,fistfuckers ,fistfucking ,fistfuckings ,fistfucks ,flange,fook,fooker,fuck,fucka,fucked,fucker,fuckers,fuckhead,fuckheads,fuckin,fucking,fuckings,fuckingshitmotherfucker,fuckme ,fucks,fuckwhit,fuckwit,fudge packer,fudgepacker,fuk,fuker,fukker,fukkin,fuks,fukwhit,fukwit,fux,fux0r,f_u_c_k,gangbang,gangbanged ,gangbangs ,gaylord,gaysex,goatse,God,god-dam,god-damned,goddamn,goddamned,hardcoresex ,hell,heshe,hoar,hoare,hoer,homo,hore,horniest,horny,hotsex,jack-off ,jackoff,jap,jerk-off ,jism,jiz ,jizm ,jizz,kawk,knob,knobead,knobed,knobend,knobhead,knobjocky,knobjokey,kock,kondum,kondums,kum,kummer,kumming,kums,kunilingus,l3i+ch,l3itch,labia,lmfao,lust,lusting,m0f0,m0fo,m45terbate,ma5terb8,ma5terbate,masochist,master-bate,masterb8,masterbat*,masterbat3,masterbate,masterbation,masterbations,masturbate,mo-fo,mof0,mofo,mothafuck,mothafucka,mothafuckas,mothafuckaz,mothafucked ,mothafucker,mothafuckers,mothafuckin,mothafucking ,mothafuckings,mothafucks,mother fucker,motherfuck,motherfucked,motherfucker,motherfuckers,motherfuckin,motherfucking,motherfuckings,motherfuckka,motherfucks,muff,mutha,muthafecker,muthafuckker,muther,mutherfucker,n1gga,n1gger,nazi,nigg3r,nigg4h,nigga,niggah,niggas,niggaz,nigger,niggers ,nob,nob jokey,nobhead,nobjocky,nobjokey,numbnuts,nutsack,orgasim ,orgasims ,orgasm,orgasms ,p0rn,pawn,pecker,penis,penisfucker,phonesex,phuck,phuk,phuked,phuking,phukked,phukking,phuks,phuq,pigfucker,pimpis,piss,pissed,pisser,pissers,pisses ,pissflaps,pissin ,pissing,pissoff ,poop,porn,porno,pornography,pornos,prick,pricks ,pron,pube,pusse,pussi,pussies,pussy,pussys ,rectum,retard,rimjaw,rimming,s hit,s.o.b.,sadist,schlong,screwing,scroat,scrote,scrotum,semen,sex,sh!+,sh!t,sh1t,shag,shagger,shaggin,shagging,shemale,shi+,shit,shitdick,shite,shited,shitey,shitfuck,shitfull,shithead,shiting,shitings,shits,shitted,shitter,shitters ,shitting,shittings,shitty ,skank,slut,sluts,smegma,smut,snatch,son-of-a-bitch,spac,spunk,s_h_i_t,t1tt1e5,t1tties,teets,teez,testical,testicle,tit,titfuck,tits,titt,tittie5,tittiefucker,titties,tittyfuck,tittywank,titwank,tosser,turd,tw4t,twat,twathead,twatty,twunt,twunter,v14gra,v1gra,vagina,viagra,vulva,w00se,wang,wank,wanker,wanky,whoar,whore,willies,willy,xrated,xxx"
}
tag "long_text" {fb.content regex_exact ".{1000,}" or fb.parent.content regex_exact ".{1000,}"}
tag "many_caps" {fb.content regex_partial "[A-Z\\\\s]{25}" or fb.parent.content regex_partial "[A-Z\\\\s]{25}"}'''


def setup(username,apikey):
    global client
    client = Client(username,apikey)
    return client

def to_timestamp(dt, epoch=datetime.datetime(1970,1,1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

def day_timestamp(d):
    return to_timestamp(datetime.datetime.combine(d, datetime.datetime.min.time()))

def now_timestamp():
    return to_timestamp(datetime.datetime.now())

def get_all():
    for rec in client.pylon.get():
        print [rec[y] for y in "name,hash,status,volume".split(',')] + [to_timestamp(rec['start'])]

def freqDist(hash,target,threshold,filter=None,start=None,end=None):

    # Get start for hash
    if start is None and end is None:
        start = to_timestamp(client.pylon.get(hash)['start'])
        end = now_timestamp()

    parameters = {'analysis_type': 'freqDist', 'parameters': {'threshold': threshold, 'target': target }}

    result = client.pylon.analyze(hash, parameters, filter=filter)

    if not result['analysis']['redacted'] and result['analysis']['results']:
        return pd.DataFrame.from_records(result['analysis']['results'],index='key')
    else:
        return None

def plot_freqDist(hash,target,threshold,filter=None,ax=None,start=None,end=None,title=None):
    df = freqDist(hash,target,threshold,filter,start=start,end=end)

    if df is None:
        print '-- Redacted --'
    else:
        if ax is None:
            df.sort(columns=['unique_authors']).plot(kind='barh',figsize=(10,5), title=title)
        else:
            df.sort(columns=['unique_authors']).plot(kind='barh', ax=ax, legend=False,title=title)

def timeSeries(hash,interval='hour',span=1,filter=None,start=None,end=None):

    if start is None and end is None:
        start = to_timestamp(client.pylon.get(hash)['start'])
        end = now_timestamp()

    parameters = {'analysis_type': 'timeSeries', 'parameters': {'interval': interval, 'span': span }}
    result = client.pylon.analyze(hash, parameters,filter,start,end)

    if not result['analysis']['redacted'] and result['analysis']['results']:
        df = pd.DataFrame.from_records(result['analysis']['results'],index='key')
        df.index=df.index.map(datetime.datetime.fromtimestamp)
        return df
    else:
        print result
        return None

def plot_timeSeries(hash,interval='hour',span=1,filter=None,ax=None,start=None,end=None,title=None):
    df = timeSeries(hash,interval,span,filter,start=start,end=end)

    if df is None:
        print '-- Redacted --'
    else:
        if ax is None:
            df.sort().plot(figsize=(10,5), title=title)
        else:
            df.sort().plot(ax=ax, title=title)

def plot_freqDist_breakdown(hash,target,threshold,breakdown_target, breakdown_threshold,filter=None):
    reference = freqDist(hash,breakdown_target,breakdown_threshold,filter)

    if reference is None:
        print '-- Redacted at top level --'
    else:
        for group in reference.index:
            temp_filter = breakdown_target + ' == "' + group + '"'

            if not filter is None:
                temp_filter = filter + ' AND ' + temp_filter

            plot_freqDist(hash,target, threshold, filter=temp_filter)

def plot_freqDist_breakdown_by_filters(hash,filters,breakdown_target, breakdown_threshold,filter=None):
    fig, axes = plt.subplots(nrows=len(filters), ncols=1)
    fig.set_figheight(25)

    withLabel = False

    for index, f in enumerate(filters):
        temp_filter = f

        if not filter is None:
            temp_filter = '(' + filter + ') AND (' + f + ')'

        plot_freqDist(hash, breakdown_target, breakdown_threshold, filter=temp_filter, ax=axes[index])

def gender_nest(hash, target, threshold, breakdown_target, breakdown_threshold,filter=None):

    df = freqDist(hash,breakdown_target,breakdown_threshold,filter)
    running=df

    if df is not None:
        nextlevel=list()
        loop=[(i,g) for i in df.index for g in "male,female".split(',')]
        for i in loop:
            csdl='%s == "%s" and fb.author.gender == "%s"' % ((breakdown_target,)+i)

            if not filter is None:
                csdl = '(' + filter + ') AND (' + csdl + ')'

            dfi = freqDist(hash,target,threshold,filter=csdl)
            nextlevel.append(dfi)
        running=pd.concat(nextlevel,keys=loop)
    running['unique_authors'].unstack().plot(kind='barh',stacked=True, figsize=(12, 12))

def amplification_breakdown(hash, breakdown_target, breakdown_threshold, story_filter_target, engagement_filter_target):
    reference = freqDist(hash,breakdown_target,breakdown_threshold)

    if reference is None:
        print '-- Redacted at top level --'
    else:
        for group in reference.index:
            amplification(hash, group,story_filter_target, engagement_filter_target)

def amplification(hash, value, story_filter_target, engagement_filter_target):
    result = pd.DataFrame(columns=['User','Page'], index=['Stories','Engagements', 'Amplification'])

    print story_filter_target + ' == "' + value + '"'

    stories = freqDist(hash,'fb.author.type', 2, filter=story_filter_target + ' == "' + value + '"')
    engagements = freqDist(hash,'fb.parent.author.type', 2, filter=engagement_filter_target + ' == "' + value + '"')

    result['User']['Stories'] = stories['unique_authors']['user']
    result['Page']['Stories'] = stories['unique_authors']['page']

    result['User']['Engagements'] = engagements['unique_authors']['user']
    result['Page']['Engagements'] = engagements['unique_authors']['page']

    result['User']['Amplification'] = float(result['User']['Engagements']) / result['User']['Stories']
    result['Page']['Amplification'] = float(result['Page']['Engagements']) / result['Page']['Stories']

    print 'Amplification result: ' + value
    print result
    print ''

def plot_age_gender_pyramid(df,figsize=(12,5),title='age-gender pyramid'): # dataframe with index ('gender','age') and 'author' column
    df.index=df.index.swaplevel(0,1)
    dfu=df['unique_authors'].unstack() # unstack the gender values into columns
    max_xlim=max(dfu['female'].max(),dfu['male'].max())
    (fig,axes)=plt.subplots(nrows=1,ncols=2,figsize=figsize)
    fig.suptitle(title,fontsize=14)
    female_subplot=dfu['female'].plot(kind='barh',ax=axes[0],color='pink')
    female_subplot.set_xlim([max_xlim,0])
    male_subplot=dfu['male'].plot(kind='barh',ax=axes[1])
    male_subplot.set_xlim([0,max_xlim])
    axes[0].set_title('FEMALE AUTHORS')
    axes[1].set_title('MALE AUTHORS')
    axes[1].set_ylabel('')
    axes[1].set_yticklabels(['' for item in axes[1].get_yticklabels()])

def age_gender_pyramid(hash,target,threshold,filter=None):
    df=freqDist(hash,target,threshold,filter)

    mf="male,female".split(',')

    if df is not None:
        for i in sorted(df.index):
            running=list()
            for g in mf:
                csdl='%s == "%s" and fb.author.gender == "%s"' % (target,i,g)

                if not filter is None:
                    csdl = '(' + filter + ') AND (' + csdl + ')'

                dfi=freqDist(hash,'fb.author.age',4,filter=csdl)
                running.append(dfi)

            pyramid=pd.concat(running,keys=mf)
            try:
                plot_age_gender_pyramid(pyramid,title=i)
            except Exception, e:
                print i,e

def plot_dashboard(hash, config):

    start = to_timestamp(client.pylon.get(hash)['start'])
    end = now_timestamp()

    fig, axes = plt.subplots(nrows=len(config), ncols=len(config[0]), figsize=(15,len(config[0])*6))
    fig.subplots_adjust(hspace=.5)

    for i, row in enumerate(config):
        for j, item in enumerate(row):
            if item[0] == 'timeSeries':
                plot_timeSeries(hash,item[1],item[2],ax=axes[i,j],start=start,end=end,title=item[3])
            else:
                plot_freqDist(hash,item[1],item[2],ax=axes[i,j],start=start,end=end,title=item[3])

def analysis_to_csv(data,filename):
    time = datetime.datetime.now()
    exists = os.path.isfile(filename)

    f = open(filename, 'a')

    if not exists:
        f.write('timestamp,key,interactions,unique_authors\n')

    for index, row in data.iterrows():
        f.write('"{0}","{1}",{2},{3}\n'.format(time, index, row['interactions'], row['unique_authors']))

    f.close()

def record_freqDist(filename,hash,target,threshold,filter=None):

    while True:
        result = freqDist(hash,target,threshold,filter)

        if not result is None:
            analysis_to_csv(result,filename)

        time.sleep(30)