import pandas as pd
import datetime
from matplotlib import gridspec
import matplotlib.pyplot as plt

def normalize_val(total, val):
    return float(val) / total

# Normalizes a column of a dataframe, so all values sum to 1
def normalize_results(df, key):
    df_copy = pd.DataFrame.copy(df,deep=True)
    total = df_copy.sum()
    df_copy['normalized'] = df.apply(lambda row: normalize_val(total, row[key]), axis=1)
    return df_copy

# Plots a timeseries from an timeseries API response
def chart_timeseries(ts_result):

    # Check result is not redacted
    if not ts_result['analysis']['redacted']:

        # Extract result data to dataframe
        ts_df = pd.DataFrame.from_records(ts_result['analysis']['results'],index='key')

        # Map the index labels to readable dates
        ts_df.index=ts_df.index.map(datetime.datetime.fromtimestamp)

        # Sort the data and plot a chart
        ts_df.sort().plot(figsize=(14,6))

# Plots a frequency distribution result from the API
def chart_freqdist(fd_result):

    # Check result is not redacted
    if not fd_result['analysis']['redacted']:

        # Extract result data to dataframe
        fd_df = pd.DataFrame.from_records(fd_result['analysis']['results'],index='key')

        # Sort the data and plot a chart
        fd_df.sort(columns=['unique_authors']).plot(kind='barh',figsize=(14,6))


# Plots an age-gender pyramid based on a nested query result
def chart_agegender(nested_result):

    # Check result is not redacted
    if not nested_result['analysis']['redacted']:

        # Build dataframe of results
        df_male = pd.DataFrame.from_records(
            nested_result['analysis']['results'][0]['child']['results'],index='key')

        df_female = pd.DataFrame.from_records(
            nested_result['analysis']['results'][1]['child']['results'],index='key')

        df_pyramid = pd.concat([df_male, df_female], axis=1, keys=['male','female'])

        # Create layout for subplots
        fig = plt.figure(figsize=(15,6))
        gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
        axes=map(plt.subplot,gs)

        # Plot charts
        #  - Note that finding the max X value across results helps us normalize the charts, and
        #  plot the female chart in reverse to create the pyramid shape
        max_xlim=max(df_pyramid[('male', 'unique_authors')].max(),df_pyramid[('female', 'unique_authors')].max())

        female_subplot=df_pyramid[('female','unique_authors')].plot(kind='barh',ax=axes[0],color='pink',alpha=0.8)
        female_subplot.set_xlim([max_xlim,0]) # This line 'reverses' the bars on the chart

        male_subplot=df_pyramid[('male', 'unique_authors')].plot(kind='barh',ax=axes[1],color='mediumblue',alpha=0.8)
        male_subplot.set_xlim([0,max_xlim])

        # Tidy up axis labels for presentation
        axes[0].set_xlabel('female authors')
        axes[1].set_xlabel('male authors')
        axes[1].set_ylabel('')
        axes[1].set_yticklabels(['' for item in axes[1].get_yticklabels()])
        for i in (0,1):
            for j in axes[i].xaxis.get_major_ticks():
                j.label.set_rotation(30)


# Plots a timeseries baselined by number of interactions
def chart_timeseries_baseline_interactions(ts_audience, ts_baseline, normalized=True):

    if not ts_audience['analysis']['redacted'] and not ts_baseline['analysis']['redacted']:

        df_audience = pd.DataFrame.from_records(ts_audience['analysis']['results'],index='key',exclude=['unique_authors'])
        df_baseline = pd.DataFrame.from_records(ts_baseline['analysis']['results'],index='key',exclude=['unique_authors'])

        # If normalization is specified normalize each dataframe before plotting
        if normalized:
            df_audience = normalize_results(df_audience, 'interactions')
            df_baseline = normalize_results(df_baseline, 'interactions')

            # Drop data we don't want to plot
            df_audience = df_audience.drop('interactions',1)
            df_baseline = df_baseline.drop('interactions',1)


        df_plot = pd.concat([df_audience,df_baseline], axis=1, keys=['audience', 'baseline'])

        df_plot.index=df_plot.index.map(datetime.datetime.fromtimestamp)
        df_plot.sort().plot(figsize=(14,6), color=['red','silver'])

# Plots a baselined freqdist based on unique_author counts
def chart_freqdist_baseline_uniqueauthors(fd_audience, fd_baseline, normalized=True):

    # Check result is not redacted
    if not fd_audience['analysis']['redacted'] and not fd_baseline['analysis']['redacted']:

        # Extract result data to dataframe
        df_audience = pd.DataFrame.from_records(fd_audience['analysis']['results'],index='key',exclude=['interactions'])
        df_baseline = pd.DataFrame.from_records(fd_baseline['analysis']['results'],index='key',exclude=['interactions'])

        # If normalization is specified normalize each dataframe before plotting
        if normalized:
            df_audience = normalize_results(df_audience, 'unique_authors')
            df_baseline = normalize_results(df_baseline, 'unique_authors')

        df_plot = pd.concat([df_audience, df_baseline], axis=1, keys=['audience', 'baseline'])

        # Choose which column to plot depending on whether the data has been normalized
        key = 'unique_authors'
        if normalized:
            key = 'normalized'

        # Sort the data and plot a chart
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(14,6))
        df_plot[('baseline',key)].plot(kind='barh',ax=axes,color='silver',width=0.8,linewidth=0)
        df_plot[('audience',key)].plot(kind='barh',ax=axes)

# Plots a baselined age-gender pyramid
def  chart_agegender_baselined(nested_audience, nested_baseline, normalized=True):
    if not nested_audience['analysis']['redacted'] and not nested_baseline['analysis']['redacted']:

        # Prepare dataframe for audience
        df_audience_male = pd.DataFrame.from_records(
            nested_audience['analysis']['results'][0]['child']['results'],index='key',exclude=['interactions'])

        df_audience_female = pd.DataFrame.from_records(
            nested_audience['analysis']['results'][1]['child']['results'],index='key',exclude=['interactions'])

        if normalized:
            df_audience_male = normalize_results(df_audience_male, 'unique_authors')
            df_audience_female = normalize_results(df_audience_female, 'unique_authors')

        df_audience = pd.concat([df_audience_male, df_audience_female], axis=1, keys=['male','female'])

        # Prepare dataframe for baseline
        df_baseline_male = pd.DataFrame.from_records(
            nested_baseline['analysis']['results'][0]['child']['results'],index='key',exclude=['interactions'])

        df_baseline_female = pd.DataFrame.from_records(
            nested_baseline['analysis']['results'][1]['child']['results'],index='key',exclude=['interactions'])

        if normalized:
            df_baseline_male = normalize_results(df_baseline_male, 'unique_authors')
            df_baseline_female = normalize_results(df_baseline_female, 'unique_authors')

        df_baseline = pd.concat([df_baseline_male, df_baseline_female], axis=1, keys=['male','female'])

        # Create plot layout
        fig = plt.figure(figsize=(15,6))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,1])
        axes=map(plt.subplot,gs)

        key = 'unique_authors'

        if normalized:
            key = 'normalized'

        # Find max X value across data sets
        max_xlim=max(df_audience[('male', key)].max(),
            df_audience[('female', key)].max(),
            df_baseline[('male', key)].max(),
            df_baseline[('male', key)].max())

        # Plot pyramid
        female_subplot=df_baseline[('female',key)].plot(kind='barh',ax=axes[0],color='silver',width=0.8,linewidth=0)
        df_audience[('female',key)].plot(kind='barh',ax=axes[0],color='pink',alpha=0.8) #royalblue
        female_subplot.set_xlim([max_xlim,0])

        male_subplot=df_baseline[('male',key)].plot(kind='barh',ax=axes[1],color='silver',width=0.8,linewidth=0)
        df_audience[('male',key)].plot(kind='barh',ax=axes[1],color='mediumblue',alpha=0.8)
        male_subplot.set_xlim([0,max_xlim])

        # Plot scatter chart of indexes
        df_indexes = pd.DataFrame(index=df_audience.index, columns=['male','female'])

        for index,row in df_indexes.iterrows():
            row['male'] = float(df_audience['male'][key][index]) / df_baseline['male'][key][index]
            row['female'] = float(df_audience['female'][key][index]) / df_baseline['female'][key][index]

        df_indexes = df_indexes.reset_index()
        df_indexes['agerank'] = df_indexes.index

        df_indexes.plot(kind='scatter',alpha=0.7,marker='o',x='female',
                  y='agerank',s=300,c='pink',ax=axes[2],ylim=(-0.5,len(df_indexes)-0.5));

        df_indexes.plot(kind='scatter',alpha=0.7,marker='o',x='male',
                  y='agerank',s=300,c='mediumblue',ax=axes[2]);

        # Tidy axis labels
        axes[0].set_xlabel('female authors')
        axes[1].set_xlabel('male authors')
        axes[1].set_ylabel('')
        axes[1].set_yticklabels(['' for item in axes[1].get_yticklabels()])
        for i in (0,1):
            for j in axes[i].xaxis.get_major_ticks():
                j.label.set_rotation(30)

        axes[2].set_ylabel('')
        axes[2].set_xlabel('index')
        axes[2].set_yticklabels(['' for item in axes[2].get_yticklabels()])
        gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])


# Plots a time series, aggregated by count of interactions in each hour
def chart_aggregated_hourly_interactions(ts_result):

    # Check result is not redacted
    if not ts_result['analysis']['redacted']:

        # Extract result data to dataframe
        df = pd.DataFrame.from_records(ts_result['analysis']['results'],index='key',exclude=['unique_authors'])
        df.index=df.index.map(datetime.datetime.fromtimestamp)

        # Aggregate results by hour
        df = pd.DataFrame(df.groupby(df.index.map(lambda t: t.hour)).interactions.sum())

        # Sort the data and plot a chart
        df.sort_index().plot(kind='bar', figsize=(14,6))

# Plots a time series, aggregated by count of interaction in each hour, set against a baseline audience
def chart_baselined_aggregated_hourly_interactions(ts_audience, ts_baseline, normalized=True):

    # Check result is not redacted
    if not ts_audience['analysis']['redacted'] and not ts_baseline['analysis']['redacted']:

        # Extract result data to dataframe
        df_audience = pd.DataFrame.from_records(ts_audience['analysis']['results'],index='key',exclude=['unique_authors'])
        df_audience.index=df_audience.index.map(datetime.datetime.fromtimestamp)
        df_baseline = pd.DataFrame.from_records(ts_baseline['analysis']['results'],index='key',exclude=['unique_authors'])
        df_baseline.index=df_baseline.index.map(datetime.datetime.fromtimestamp)

        # Aggregate results by hour
        df_audience = pd.DataFrame(df_audience.groupby(df_audience.index.map(lambda t: t.hour)).interactions.sum())
        df_baseline = pd.DataFrame(df_baseline.groupby(df_baseline.index.map(lambda t: t.hour)).interactions.sum())

        # If normalization is specified normalize each dataframe before plotting
        if normalized:
            df_audience = normalize_results(df_audience, 'interactions')
            df_baseline = normalize_results(df_baseline, 'interactions')

        df_plot = pd.concat([df_audience, df_baseline], axis=1, keys=['audience', 'baseline'])

        # Choose which column to plot depending on whether the data has been normalized
        key = 'interactions'
        if normalized:
            key = 'normalized'

        # Sort the data and plot a chart
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(14,6))
        df_plot[('baseline',key)].sort_index().plot(kind='bar',ax=axes,color='silver',width=0.8,linewidth=0)
        df_plot[('audience',key)].sort_index().plot(kind='bar',ax=axes)