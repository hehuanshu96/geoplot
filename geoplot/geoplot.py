"""
This module defines the majority of geoplot functions, including all plot types.
"""

import geopandas as gpd
from geopandas.plotting import __pysal_choro, norm_cmap
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import warnings
from geoplot.quad import QuadTree
import shapely.geometry
import pandas as pd


def pointplot(df, projection=None,
              hue=None, categorical=False, scheme=None, k=None, cmap='Set1', vmin=None, vmax=None,
              scale=None, limits=(0.5, 2), scale_func=None,
              legend=False, legend_values=None, legend_labels=None, legend_kwargs=None,
              figsize=(8, 6), extent=None, ax=None, **kwargs):
    """
    A geospatial scatter plot. The simplest useful plot type available.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The data column whose entries are being discretely colorized. May be passed in any of a number of flexible
        formats. Defaults to None, in which case no colormap will be applied at all.
    categorical : boolean, optional
        Whether the inputted ``hue`` is already a categorical variable or not. Defaults to False. Ignored if ``hue``
        is set to None or not specified.
    scheme : None or {"quartiles"|"quantiles"|"equal_interval"|"fisher_jenks"} (?), optional
        The PySAL scheme which will be used to determine categorical bins for the ``hue`` choropleth. If ``hue`` is
        left unspecified or set to None this variable is ignored.
    k : int, optional
        If ``hue`` is specified and ``categorical`` is False, this number, set to 5 by default, will determine how
        many bins will exist in the output visualization. If ``hue`` is left unspecified or set to None this
        variable is ignored.
    cmap : matplotlib color, optional
        The string representation for a matplotlib colormap to be applied to this dataset. ``hue`` must be non-empty
        for a colormap to be applied at all, so this parameter is ignored otherwise.
    vmin : float, optional
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value.
    vmax : float, optional
        A strict ceiling on the value associated with the "top" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value.
    scale : str or iterable, optional
        The data parameter against which the geometries will be scaled.
    limits : (min, max) tuple, optional
        The minimum and maximum limits against which the shape will be scaled.
    scale_func : unfunc, optional
        The default scaling function is a linear one. You can change the scaling function to whatever you want by
        specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
        maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.
    legend : boolean, optional
        Whether or not to include a legend in the output plot. This parameter will be ignored if ``hue`` is set to
        None or left unspecified.
    legend_values : list, optional
        This variable will only have an effect if the ``scale`` parameter is in use (e.g. size is a variable) and
        ``legend=True``. Equal intervals will be used for the "points" in the legend by default. However,
        particularly if your scale is non-linear, oftentimes this isn't what you want. If this variable is provided as
        well, the values included in the input will be used by the legend instead.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to the values.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to the ``matplotlib`` ``ax.legend`` method. For a list of possible arguments
        refer to the `the matplotlib documentation
        <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.



    Examples
    --------

    The most basic plot possible is little more than a bunch of points and a projection:

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.pointplot(points, projection=ccrs.PlateCarree())

    .. image:: ../figures/pointplot/pointplot-initial.png


    Use the ``hue`` parameter to apply a colormap to the data:

    .. code-block:: python

        gplt.pointplot(cities, projection=ccrs.AlbersEqualArea(), hue='ELEV_IN_FT')

    .. image:: ../figures/pointplot/pointplot-hue.png

    The ``legend`` parameter toggles a legend.

    .. code-block:: python

        gplt.pointplot(cities, projection=ccrs.AlbersEqualArea(), hue='ELEV_IN_FT', legend=True)

    .. image:: ../figures/pointplot/pointplot-legend.png

    ``legend_labels`` specifies custom legend labels.

    .. code-block:: python

        gplt.pointplot(cities, projection=ccrs.AlbersEqualArea(), hue='ELEV_IN_FT',
                       legend=True, legend_labels=list('ABCDE'))

    .. image:: ../figures/pointplot/pointplot-legend-labels.png


    ``pointplot`` will default to binning the observations in the given data column into five ordinal classes. Bins
    are optimized to contain approximately equal numbers of observations by default (they are "quartiles"). You can
    also specify an alternative binning scheme using the ``scheme`` parameter.

    This can produce very different results. You must have ``pysal`` installed in order for this parameter to work.

    .. code-block:: python

        gplt.pointplot(cities, projection=ccrs.AlbersEqualArea(), hue='ELEV_IN_FT',
                       legend=True, scheme='equal_interval')

    .. image:: ../figures/pointplot/pointplot-scheme.png

    If your data is already `categorical <http://pandas.pydata.org/pandas-docs/stable/categorical.html>`_,
    you can specify ``categorical=True`` to instead use the labels in your dataset directly.

    .. code-block:: python

        gplt.pointplot(collisions, projection=ccrs.AlbersEqualArea(), hue='BOROUGH',
                       legend=True, categorical=True)

    .. image:: ../figures/pointplot/pointplot-categorical.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These arguments, often
    necessary to properly position the legend, will be passed to the underlying `matplotlib Legend instance
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.

    .. code-block:: python

        gplt.pointplot(collisions, projection=ccrs.AlbersEqualArea(), hue='BOROUGH',
                       categorical=True, legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-legend-kwargs.png

    Additional arguments will be interpreted as keyword arguments to the underlying `matplotlib scatter
    <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_ plot.

    .. code-block:: python

        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()], projection=ccrs.AlbersEqualArea(),
                       hue='BOROUGH', categorical=True,
                       legend=True, legend_kwargs={'loc': 'upper left'},
                       edgecolor='white', linewidth=0.5)

    .. image:: ../figures/pointplot/pointplot-kwargs.png

    Change the number of data bins used by specifying an alternative ``k`` value.

    .. code-block:: python

        gplt.pointplot(data, projection=ccrs.AlbersEqualArea(),
                       hue='var', k=8,
                       edgecolor='white', linewidth=0.5,
                       legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)})

    .. image:: ../figures/pointplot/pointplot-k.png

    Adjust the `colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to any
    matplotlib-recognizable colormap using the ``cmap`` parameter:

    .. code-block:: python

        gplt.pointplot(data, projection=ccrs.AlbersEqualArea(),
               hue='var', cmap='inferno', k=8,
               edgecolor='white', linewidth=0.5,
               legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)})


    .. image:: ../figures/pointplot/pointplot-cmap.png

    ``pointplot`` also supports using point ``scale`` as a visual variable.

    .. code-block:: python

        gplt.pointplot(collisions, projection=ccrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED',
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-scale.png

    The default limits, ``(0.5, 2.0)``, can be adjusted via the ``limits`` parameter.(usually a less conservative
    value is appropriate).

    .. code-block:: python

        gplt.pointplot(collisions, projection=ccrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED', limits=(0, 10),
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-limits.png

    The default scaling function is a linear one. You can change the scaling function to whatever you want by
    specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
    maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.

    .. code-block:: python

        def trivial_scale(minval, maxval):
            def scalar(val):
                return 2
            return scalar

        gplt.pointplot(collisions, projection=ccrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED', scale_func=trivial_scale,
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-scale-func.png

    ``hue`` and ``scale`` can co-exist. Note, however, that only the ``hue`` legend will be displayed in this case.

    .. code-block:: python

        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()],
                       projection=ccrs.AlbersEqualArea(),
                       hue='BOROUGH', categorical=True,
                       scale='NUMBER OF PERSONS INJURED', limits=(0, 10),
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-hue-scale.png
    """
    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # TODO: Work this out.
    # In that case we can return a `matplotlib` plot directly.
    if not projection:
        raise NotImplementedError
        # xs = np.array([p.x for p in df.geometry])
        # ys = np.array([p.y for p in df.geometry])
        # return plt.scatter(xs, ys)

    # Properly set up the projection.
    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
        'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Set extent.
    xs = np.array([p.x for p in df.geometry])
    ys = np.array([p.y for p in df.geometry])

    if extent:
        ax.set_extent(extent)
    else:
        # xs = np.array([p.x for p in df.geometry])
        # ys = np.array([p.y for p in df.geometry])
        # ax.set_extent((np.min(xs), np.max(xs), np.min(ys), np.max(ys)))
        pass  # Default extent.

    # Check if the ``scale`` parameter is filled, and use it to fill a ``values`` name.
    if scale:
        if isinstance(scale, str):
            scalar_values = df[scale]
        else:
            scalar_values = scale

        # Compute a scale function.
        dmin, dmax = np.min(scalar_values), np.max(scalar_values)
        if not scale_func:
            dslope = (limits[1] - limits[0]) / (dmax - dmin)
            dscale = lambda dval: limits[0] + dslope * (dval - dmin)
        else:
            dscale = scale_func(dmin, dmax)

        # Apply the scale function.
        scalar_multiples = np.array([dscale(d) for d in scalar_values])
        sizes = scalar_multiples * 20

        # Draw a legend, if appropriate.
        if legend:
            _paint_carto_legend(ax, scalar_values, legend_values, legend_labels, dscale, legend_kwargs)
    else:
        sizes = 20  # pyplot default

    # Clean up patches.
    _lay_out_axes(ax)

    # If a hue parameter is specified and is a string, convert it to a reference to its column.
    if isinstance(hue, str):
        hue = df[hue]

    # Validate bucketing.
    categorical, k, scheme = _validate_buckets(categorical, k, scheme)

    if hue is not None:
        cmap, categories, hue_values = _discrete_colorize(categorical, hue, scheme, k, cmap, vmin, vmax)
        colors = [cmap.to_rgba(v) for v in hue_values]

        if legend:
            _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
    else:
        colors = 'steelblue'

    # Draw.
    ax.scatter(xs, ys, transform=ccrs.PlateCarree(), c=colors, s=sizes, **kwargs)

    return ax


def polyplot(df, projection=None,
             extent=None,
             figsize=(8, 6), ax=None,
             facecolor='None', **kwargs):
    """
    Trivially plots whatever geometries are passed to it. Mostly meant to be used in concert with other,
    more interesting plot types.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    facecolor : matplotlib color, optional
        The color that will be used for the fill "inside" of the polygon. This parameter defaults to the string
        ``'None'``, which creates transparent polygons.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------

    A trivial example can be created with just two parameters, a geometry and a projection.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea())


    .. image:: ../figures/polyplot/polyplot-initial.png

    However, note that ``polyplot`` is mainly intended to be used in concert with other plot types.

    .. code-block:: python

        ax = gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea())
        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()], projection=ccrs.AlbersEqualArea(),
                       hue='BOROUGH', categorical=True,
                       legend=True, edgecolor='white', linewidth=0.5, legend_kwargs={'loc': 'upper left'},
                       ax=ax)


    .. image:: ../figures/polyplot/polyplot-stacked.png
    """
    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # In this case we can return a `matplotlib` plot directly.
    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
        'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Set extent.
    x_min_coord, x_max_coord, y_min_coord, y_max_coord = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    # import pdb; pdb.set_trace()
    if extent:
        ax.set_extent(extent)
    else:
        ax.set_extent((x_min_coord, x_max_coord, y_min_coord, y_max_coord))

    # Clean up patches.
    _lay_out_axes(ax)

    # Finally we draw the features.
    for geom in df.geometry:
        features = ShapelyFeature([geom], ccrs.PlateCarree())
        ax.add_feature(features, facecolor=facecolor, **kwargs)

    return ax


def choropleth(df, projection=None,
               hue=None,
               scheme=None, k=None, cmap='Set1', categorical=False, vmin=None, vmax=None,
               legend=False, legend_kwargs=None, legend_labels=None,
               extent=None,
               figsize=(8, 6), ax=None,
               **kwargs):
    """
    A simple aggregation plot based on geometry.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The data column whose entries are being discretely colorized. May be passed in any of a number of flexible
        formats. Defaults to None, in which case no colormap will be applied at all.
    categorical : boolean, optional
        Whether the inputted ``hue`` is already a categorical variable or not. Defaults to False. Ignored if ``hue``
        is set to None or not specified.
    scheme : None or {"quartiles"|"quantiles"|"equal_interval"|"fisher_jenks"} (?), optional
        The PySAL scheme which will be used to determine categorical bins for the ``hue`` choropleth. If ``hue`` is
        left unspecified or set to None this variable is ignored.
    k : int, optional
        If ``hue`` is specified and ``categorical`` is False, this number, set to 5 by default, will determine how
        many bins will exist in the output visualization. If ``hue`` is left unspecified or set to None this
        variable is ignored.
    cmap : matplotlib color, optional
        The string representation for a matplotlib colormap to be applied to this dataset. ``hue`` must be non-empty
        for a colormap to be applied at all, so this parameter is ignored otherwise.
    vmin : float, optional
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value.
    vmax : float, optional
        A strict ceiling on the value associated with the "top" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value.
    legend : boolean, optional
        Whether or not to include a legend in the output plot. This parameter will be ignored if ``hue`` is set to
        None or left unspecified.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to the values.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to the ``matplotlib`` ``ax.legend`` method. For a list of possible arguments
        refer to `the matplotlib documentation
        <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------

    A basic choropleth specifies a collection of polygons, a projection, and a ``hue`` variable to colorize with.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.choropleth(polydata, hue='latdep', projection=ccrs.PlateCarree())

    .. image:: ../figures/choropleth/choropleth-initial.png


    You can change the colormap with the ``cmap`` parameter.

    .. code-block:: python

        gplt.choropleth(polydata, hue='latdep', projection=ccrs.PlateCarree(), cmap='Blues')

    .. image:: ../figures/choropleth/choropleth-cmap.png

    If your data column is already categorical, you can use its values directly by specifying the ``categorical``
    parameter.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=ccrs.AlbersEqualArea(), hue='BoroName', categorical=True)

    .. image:: ../figures/choropleth/choropleth-categorical.png

    To add a legend, specify ``legend``.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=ccrs.AlbersEqualArea(), hue='BoroName',
                        categorical=True, legend=True)

    .. image:: ../figures/choropleth/choropleth-legend.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These arguments, often
    necessary to properly position the legend, will be passed to the underlying `matplotlib Legend instance
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=ccrs.AlbersEqualArea(), hue='BoroName',
                        categorical=True, legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/choropleth/choropleth-legend-kwargs.png

    Additional arguments not in the method signature will be passed as keyword parameters to the underlying
    `matplotlib Polygon patches <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=ccrs.AlbersEqualArea(), hue='BoroName', categorical=True,
                        linewidth=0)

    .. image:: ../figures/choropleth/choropleth-kwargs.png

    Choropleths default to splitting the data into five buckets with approximately equal numbers of observations in
    them. Change the number of buckets by specifying ``k``.

    .. code-block:: python

        gplt.choropleth(census_tracts, hue='mock_data', projection=ccrs.AlbersEqualArea(),
                legend=True, edgecolor='white', linewidth=0.5, legend_kwargs={'loc': 'upper left'},
                k=2)

    .. image:: ../figures/choropleth/choropleth-k.png

    ``legend_labels`` controls the legend labels.

    .. code-block:: python

        gplt.choropleth(census_tracts, hue='mock_data', projection=ccrs.AlbersEqualArea(),
                        edgecolor='white', linewidth=0.5,
                        legend=True, legend_kwargs={'loc': 'upper left'},
                        legend_labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])

    .. image:: ../figures/choropleth/choropleth-legend-labels.png

    Alternatively, change the scheme used to generate the buckets with the ``scheme`` parameter. ``equal_interval``,
    for example, will generate buckets of equal data distribution size instead.

    .. code-block:: python

        gplt.choropleth(census_tracts, hue='mock_data', projection=ccrs.AlbersEqualArea(),
                legend=True, edgecolor='white', linewidth=0.5, legend_kwargs={'loc': 'upper left'},
                scheme='equal_interval')

    .. image:: ../figures/choropleth/choropleth-scheme.png
    """

    # Format the data to be displayed for input.
    hue = _validate_hue(df, hue)

    # Validate bucketing.
    categorical, k, scheme = _validate_buckets(categorical, k, scheme)

    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # In this case we can return a `matplotlib` plot directly.
    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
        'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Set extent.
    x_min_coord, x_max_coord, y_min_coord, y_max_coord = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    if extent:
        ax.set_extent(extent)
    else:
        ax.set_extent((x_min_coord, x_max_coord, y_min_coord, y_max_coord))

    # Generate colormaps.
    cmap, categories, values = _discrete_colorize(categorical, hue, scheme, k, cmap, vmin, vmax)

    # Clean up patches.
    _lay_out_axes(ax)

    if legend:
        _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)

    # Finally we draw the features.
    for cat, geom in zip(values, df.geometry):
        features = ShapelyFeature([geom], ccrs.PlateCarree())
        ax.add_feature(features, facecolor=cmap.to_rgba(cat), **kwargs)

    return ax


def aggplot(df, projection=None,
            hue=None,
            by=None,
            geometry=None,
            nmax=None, nmin=None, nsig=0,
            agg=np.mean,
            cmap='viridis', vmin=None, vmax=None,
            legend=True, legend_kwargs=None,
            extent=None,
            figsize=(8, 6), ax=None,
            **kwargs):
    """
    A minimum-expectations summary plot type which handles mixes of geometry types and missing aggregate geometry data.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The data column whose entries are being discretely colorized. May be passed in any of a number of flexible
        formats. Defaults to None, in which case no colormap will be applied at all.
    by : iterable or str, optional
        The name of a column within the dataset corresponding with some sort of geometry to aggregate points by.
        Specifying ``by`` kicks ``aggplot`` into convex hull plotting mode.
    geometry : GeoDataFrame or GeoSeries, optional
        A ``geopandas`` object containing geometries. When both ``by`` and ``geometry`` are provided ``aggplot``
        plots in geometry plotting mode, matching points in the ``by`` column with the geometries given by their index
        label in the ``geometry`` column, aggregating those, and plotting the results.
    nmax : int or None, optional
        This variable will only be used if the plot is functioning in quadtree mode; if it is not, the value here
        will be ignored. This variable specifies the maximum number of observations that will be contained in each
        quadrangle; any quadrangle containing more than ``nmax`` observations will be forcefully partitioned.

        This is useful as a way of "forcing" the quadtree to subpartition further than it would otherwise,
        as using a minimum-obsevations rule alone will cause partitioning to halt early whenever a hole in the data
        is found. For those familiar with them, an analog may be drawn here to splitting rules in decision trees.

        This variable may be left unspecified, in which case no maximum splitting rule will be used. If this
        value is specified it is enforced more strictly than the minimum splitting ``nmin`` parameter, and may result
        in partitions containing no or statistically insignificant amounts of points.
    nmin : int, optional
        This variable will only be used if the plot is functioning in quadtree mode; if it is not, the value here
        will be ignored.

        This value specifies the minimum number of observations that must be present in each quadtree split for the
        split to be followed through. For example, if we specify a value of 5, partition a quadrangle, and find that it
        contains a subquadrangle with just 4 points inside, this rule will cause the algorithm to return the parent
        quadrangle instead of its children.

        This is the primary variable controlling how deep a quadtree partition can go. Note that if ``nmax`` is
        specified that rule is given higher priority.
    nsig : int, optional
        A floor on the number of observations in an aggregation that gets reported. Aggregations containing fewer than
        ``nsig`` points are not aggregated and are instead returned as white patches, indicative of their status as
        "empty" spaces. This value defaults to 0. It should be set higher than that if one wishes to control for
        outliers.
    agg : function, optional
        The aggregation ufunc that will be applied to the ``numpy`` array of values for the variable of interest of
        observations inside of each quadrangle. Defaults to ``np.mean``. Other options are ``np.median``,
        ``np.count``, etc.
    cmap : matplotlib color, optional
        The string representation for a matplotlib colormap to be applied to this dataset. ``hue`` must be non-empty
        for a colormap to be applied at all, so this parameter is ignored otherwise.
    vmin : float, optional
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value.
    vmax : float, optional
        A strict ceiling on the value associated with the "top" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value.
    legend : boolean, optional
        Whether or not to include a legend in the output plot. This parameter will be ignored if ``hue`` is set to
        None or left unspecified.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to the ``matplotlib`` ``ax.colorbar`` method. For a list of possible arguments
        refer to `the matplotlib documentation
        <http://matplotlib.org/api/colorbar_api.html#matplotlib.colorbar.Colorbar>`_.
        http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    gridlines : boolean, optional
        Whether or not to overlay cartopy's computed latitude-longitude gridlines.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------
    This plot type is intricate: it accepts all geometry types, including a mixture of points and polygons if you
    have them, unlike most of the other plot types included in this library; and its end result can fall into any of
    three general patterns of output.

    When you have a number of geometries but are unable or unwilling (given time and/or interest constraints) to
    provide geospatial context for them, ``aggplot`` will lump your observations into a recursive quadtree. Each of
    the boxes in your result will contain in between some minimum and some maximum number of observations.

    To start with, here's an aggplot with a minimal amount of information provided, just data, a projection,
    and a data column:

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.aggplot(collisions, projection=ccrs.PlateCarree(), hue='LATDEP')

    .. image:: ../figures/aggplot/aggplot-initial.png

    Quadtree decompositions look a bit like abstract paintings, but they do succeed in getting a point across. To
    get the best output, you often need to tweak the ``nmin`` and ``nmax`` parameters, controlling the minimum and
    maximum number of observations per box, respectively, yourself. Changing the ``cmap`` can also be helpful.

    .. code-block:: python

        gplt.aggplot(collisions, nmin=20, nmax=500, projection=ccrs.PlateCarree(), hue='LATDEP', cmap='Blues')

    .. image:: ../figures/aggplot/aggplot-quadtree.png

    Note that ``aggplot`` will satisfy the ``nmax`` parameter before trying to satisfy ``nmin``, so you may result in
    spaces without observations, or ones lacking a statistically significant number of observations. This is
    necessary in order to break up "spaces" that the algorithm would otherwise end on. You can control the
    maximum number of observations in the holes using the ``nsig`` parameter.

    .. code-block:: python

        gplt.aggplot(collisions, nmin=20, nmax=500, nsig=5, projection=ccrs.PlateCarree(), hue='LATDEP', cmap='Reds')

    .. image:: ../figures/aggplot/aggplot-quadtree-tuned.png

    Usually you'll just have to play around with these parameters to get the clearest picture.

    If you can provide some sense of space in the form of a categorical variable, you can get a more readable
    picture using convex hull -calculated spaces by passing that variable into the ``by`` parameter.

    .. code-block:: python

        gplt.aggplot(collisions[collisions['ZIP CODE'].notnull()], projection=ccrs.PlateCarree(),
                 hue='LATDEP', by='ZIP CODE', cmap='Greens')

    .. image:: ../figures/aggplot/aggplot-hulls.png

    Finally, if you actually know exactly the geometries that you would like to aggregate by, and can provide a
    ``GeoSeries`` whose index matches your categorical variable of interest, then you can generate an exact
    choropleth.

    .. code-block:: python

        gplt.aggplot(collisions, projection=ccrs.PlateCarree(), hue='NUMBER OF PERSONS INJURED', cmap='Reds',
                     geometry=boroughs_2, by='BOROUGH', agg=np.max)

    .. image:: ../figures/aggplot/aggplot-by.png

    Note also the usage of the ``agg`` parameter, which controls what you mean by the "agg" in ``aggplot``. By
    default it will be the mean of the observations contained in the polygon, but you can also specify an
    alternative metric, like the use of ``np.max`` instead here.

    """

    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
        'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
    })

    fig = plt.plot(figsize=figsize)
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Clean up patches.
    _lay_out_axes(ax)

    # Format hue and generate a colormap
    hue_col = hue
    values = _validate_hue(df, hue)
    cmap = _continuous_colormap(values, cmap, vmin, vmax)

    if geometry is not None and by is None:
        raise NotImplementedError("Aggregation by geometry alone is not currently implemented and unlikely to be "
                                  "implemented in the future - it is likely out-of-scope here due to the algorithmic "
                                  "complexity involved.")
        # The user wants us to classify our data geometries by their location within the passed world geometries
        # ("sectors"), aggregate a statistic based on that, and return a plot. Unfortunately this seems to be too
        # hard for the moment. Two reasons:
        # 1. The Shapely API for doing so is just about as consistent as can be, but still a little bit inconsistent.
        #    In particular, it is not obvious what to do with invalid and self-intersecting geometric components passed
        #    to the algorithm.
        # 2. Point-in-polygon and, worse, polygon-in-polygon algorithms are extremely slow, to the point that almost
        #    any optimizations that the user can make by doing classification "by hand" is worth it.
        # There should perhaps be a separate library or ``geopandas`` function for doing this.

    elif by:
        bxmin = bxmax = bymin = bymax = None

        # Side-convert geometry for ease of use.
        if geometry is not None:
            # Downconvert GeoDataFrame to GeoSeries objects.
            if isinstance(geometry, gpd.GeoDataFrame): geometry = geometry.geometry

            # Valid polygons are simple polygons (``shapely.geometry.Polygon``) and complex multi-piece polygons
            # (``shapely.geometry.MultiPolygon``). The latter is an iterable of its components, so if the shape is
            # a ``MultiPolygon``, append it as that list. Otherwise if the shape is a basic ``Polygon``,
            # append a list with one element, the ``Polygon`` itself.
            def geom_convert(geom):
                if isinstance(geom, shapely.geometry.MultiPolygon):
                    return shapely.ops.cascaded_union([p for p in geom])
                elif isinstance(geom, shapely.geometry.Polygon):
                    return [geom]
                else:  # Anything else, raise.
                    raise ValueError("Shapely geometries of Polygon or MultiPolygon types are expected, but one of {0} "
                                     "type was provided.".format(type(geom)))

            geometry = geometry.map(geom_convert)

        for label, p in df.groupby(by):
            if geometry is not None:
                try:
                    sector = geometry.loc[label]
                except IndexError:
                    raise IndexError("Data contains a '{0}' label which lacks a corresponding value in the provided "
                                     "geometry.".format(label))
            else:
                sector = shapely.geometry.MultiPoint(p.geometry).convex_hull

            # Because we have to set the extent ourselves, we have to do some bookkeeping to keep track of the
            # extrema of the hulls we are generating.
            if not extent:
                if not isinstance(sector.envelope, shapely.geometry.Point):
                    hxmin, hxmax, hymin, hymax = _get_envelopes_min_maxes(pd.Series(sector.envelope.exterior))
                    if not bxmin or hxmin < bxmin:
                        bxmin = hxmin
                    if not bxmax or hxmax > bxmax:
                        bxmax = hxmax
                    if not bymin or hymin < bymin:
                        bymin = hymin
                    if not bymax or hymax > bymax:
                        bymax = hymax

            # We draw here.
            color = cmap.to_rgba(agg(p[hue_col])) if len(p) > nsig else "white"
            features = ShapelyFeature([sector], ccrs.PlateCarree())
            ax.add_feature(features, facecolor=color, **kwargs)

        # Set the extent.
        if extent:
            ax.set_extent(extent)
        else:
            ax.set_extent((bxmin, bxmax, bymin, bymax))

    else:
        # Set reasonable defaults for the n-params if appropriate.
        nmax = nmax if nmax else len(df)
        nmin = nmin if nmin else np.min([20, int(0.05 * len(df))])

        # Generate a quadtree.
        quad = QuadTree(df)
        bxmin, bxmax, bymin, bymax = quad.bounds
        # Assert that nmin is not smaller than the largest number of co-located observations (otherwise the algorithm
        # would continue running until the recursion limit).
        max_coloc = np.max([len(l) for l in quad.agg.values()])
        if max_coloc > nmin:
            raise ValueError("nmin is set to {0}, but there is a coordinate containing {1} observations in the "
                             "dataset.".format(nmin, max_coloc))
        # Run the partitions, then paint the results.
        partitions = quad.partition(nmin, nmax)
        for p in partitions:
            xmin, xmax, ymin, ymax = p.bounds
            rect = shapely.geometry.Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
            feature = ShapelyFeature([rect], ccrs.PlateCarree())
            color = cmap.to_rgba(agg(p.data[hue_col])) if p.n > nsig else "white"
            ax.add_feature(feature, facecolor=color, **kwargs)
            # TODO: The code snippet for matplotlib alone is below.
            # ax.add_artist(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='lightgray'))
            # Note: patches.append(...); ax.add_collection(PatchCollection(patches)) will not work.
            # cf. http://stackoverflow.com/questions/10550477/how-do-i-set-color-to-rectangle-in-matplotlib
        if extent:
            ax.set_extent(extent)
        else:
            ax.set_extent((bxmin, bxmax, bymin, bymax))

    # Append a legend, if appropriate.
    if legend:
        _paint_colorbar_legend(ax, values, cmap, legend_kwargs)

    return ax


def cartogram(df, projection=None,
              scale=None, limits=(0.2, 1), scale_func=None, trace=True, trace_kwargs=None,
              legend=False, legend_values=None, legend_labels=None, legend_kwargs=None,
              extent=None,
              figsize=(8, 6), ax=None,
              **kwargs):
    """
    This plot scales the size of polygonal inputs based on the value of a particular data parameter.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    scale : str or iterable, optional
        The data parameter against which the geometries will be scaled.
    limits : (min, max) tuple, optional
        The minimum and maximum limits against which the shape will be scaled.
    scale_func : unfunc, optional
        The default scaling function is a linear one. You can change the scaling function to whatever you want by
        specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
        maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.
    trace : boolean, optional
        Whether or not to include a trace of the polygon's original outline in the plot result.
    trace_kwargs : dict, optional
        If ``trace`` is set to ``True``, this parameter can be used to adjust the properties of the trace outline. This
        parameter is ignored if trace is ``False``.
    legend : boolean, optional
        Whether or not to include a legend in the output plot. This parameter will be ignored if ``hue`` is set to
        None or left unspecified.
    legend_values : list, optional
        If a legend is specified, equal intervals will be used for the "points" in the legend by default. However,
        particularly if your scale is non-linear, oftentimes this isn't what you want. If this variable is provided as
        well, the values included in the input will be used by the legend instead.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to
    legend_kwargs : dict, optional
        Keyword arguments to be passed to the ``matplotlib`` ``ax.legend`` method. For a list of possible arguments
        refer to `the matplotlib documentation
        <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------
    A basic cartogram specifies data, a projection, and a ``scale`` parameter.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea())

    .. image:: ../figures/cartogram/cartogram-initial.png

    The gray outline can be turned off by specifying ``trace``, and a legend can be added by specifying ``legend``.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       trace=False, legend=True)

    .. image:: ../figures/cartogram/cartogram-trace-legend.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These arguments, often
    necessary to properly position the legend, will be passed to the underlying `matplotlib Legend instance
    http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend`_.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       trace=False, legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/cartogram/cartogram-legend-kwargs.png

    Specify an alternative legend display using the ``legend_values`` and ``legend_labels`` parameters.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(), legend=True,
               legend_values=[2.32779655e-07, 6.39683197e-07, 1.01364661e-06, 1.17380941e-06, 2.33642596e-06][::-1],
               legend_labels=['Manhattan', 'Brooklyn', 'Queens', 'The Bronx', 'Staten Island'],
               legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/cartogram/cartogram-legend-labels.png

    Additional arguments to ``cartogram`` will be interpreted as keyword arguments for the scaled polygons,
    using `matplotlib Polygon patch
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_ rules.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       edgecolor='darkgreen')

    .. image:: ../figures/cartogram/cartogram-kwargs.png

    Manipulate the outlines use the ``trace_kwargs`` argument, which accepts the same `matplotlib Polygon patch
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_ parameters.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       trace_kwargs={'edgecolor': 'lightgreen'})

    .. image:: ../figures/cartogram/cartogram-trace-kwargs.png

    By default, the polygons will be scaled according to the data such that the minimum value is scaled by a factor of
    0.2 while the largest value is left unchanged. Adjust this using the ``limits`` parameter.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       limits=(0.5, 1))

    .. image:: ../figures/cartogram/cartogram-limits.png

    The default scaling function is a linear one. You can change the scaling function to whatever you want by
    specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
    maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.

    .. code-block:: python

        def trivial_scale(minval, maxval):
            def scalar(val):
                return 0.5
            return scalar

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       limits=(0.5, 1), scale_func=trivial_scale)

    .. image:: ../figures/cartogram/cartogram-scale-func.png
    """
    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # In this case return amatplotlib` plot directly.
    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    # Check that the ``scale`` parameter is filled, and use it to fill a ``values`` name.
    if not scale:
        raise ValueError("No scale parameter provided.")
    elif isinstance(scale, str):
        values = df[scale]
    else:
        values = scale

    # Load the projection.
    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
        'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Set extent.
    x_min_coord, x_max_coord, y_min_coord, y_max_coord = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    if extent:
        ax.set_extent(extent)
    else:
        ax.set_extent((x_min_coord, x_max_coord, y_min_coord, y_max_coord))

    # Clean up patches.
    _lay_out_axes(ax)

    # Compute a scale function.
    dmin, dmax = np.min(values), np.max(values)
    if not scale_func:
        dslope = (limits[1] - limits[0]) / (dmax - dmin)
        dscale = lambda dval: limits[0] + dslope * (dval - dmin)
    else:
        dscale = scale_func(dmin, dmax)

    # Create a legend, if appropriate.
    if legend:
        _paint_carto_legend(ax, values, legend_values, legend_labels, dscale, legend_kwargs)

    # Manipulate trace_kwargs.
    if trace:
        if trace_kwargs is None:
            trace_kwargs = dict()
        if 'edgecolor' not in trace_kwargs.keys():
            trace_kwargs['edgecolor'] = 'lightgray'
        if 'facecolor' not in trace_kwargs.keys():
            trace_kwargs['facecolor'] = 'None'

    # Manipulate kwargs.
    if 'facecolor' not in kwargs.keys():
        kwargs['facecolor'] = 'None'

    # Draw traces first, if appropriate.
    if trace:
        for polygon in df.geometry:
            features = ShapelyFeature([polygon], ccrs.PlateCarree())
            ax.add_feature(features, **trace_kwargs)

    # Finally, draw the scaled geometries.
    for value, polygon in zip(values, df.geometry):
        scale_factor = dscale(value)
        scaled_polygon = shapely.affinity.scale(polygon, xfact=scale_factor, yfact=scale_factor)
        features = ShapelyFeature([scaled_polygon], ccrs.PlateCarree())
        ax.add_feature(features, **kwargs)

    return ax


def kdeplot(df, projection=None,
            extent=None,
            figsize=(8, 6), ax=None,
            clip=None,
            **kwargs):
    """
    Geographic kernel density estimate plot.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    clip : iterable or GeoSeries, optional
        An iterable of geometries that the KDE plot will be clipped to. This is a visual parameter useful for
        "cleaning up" the plot. This feature has not yet actually been implemented!
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``sns.kdeplot`` method doing the plotting. For a list of possible
        arguments refer to `the seaborn documentation
        <http://seaborn.pydata.org/generated/seaborn.kdeplot.html>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------
    A basic `kernel density estimate <https://en.wikipedia.org/wiki/Kernel_density_estimation>`_ plot specifies data
    and a projection.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.kdeplot(collisions, projection=ccrs.AlbersEqualArea())

    .. image:: ../figures/kdeplot/kdeplot_demo_1.png

    However, kdeplots need additional geospatial context to be interpretable. In this case (and for the remainder of
    the examples) we will provide this by overlaying borough geometry.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=ccrs.AlbersEqualArea())
        gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot_demo_2.png

    Most of the rest of the parameters to ``kdeplot`` are parameters inherited from `the seaborn method by the same
    name <http://seaborn.pydata.org/generated/seaborn.kdeplot.html#seaborn.kdeplot>`_, on which this plot type is
    based. For example, specifying ``shade=True`` provides a filled KDE instead of a contour one:

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=ccrs.AlbersEqualArea(),
                          shade=True)
        gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot_demo_3.png

    Use ``n_levels`` to specify the number of contour levels.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=ccrs.AlbersEqualArea(),
                          n_levels=30)
        gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot_demo_4.png

    Or specify ``cmap`` to change the colormap.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=ccrs.AlbersEqualArea(),
             cmap='Purples')
        gplt.polyplot(boroughs, projection=ccrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot_demo_5.png

    """
    import seaborn as sns  # Immediately fail if no seaborn.
    sns.reset_orig()  # Reset to default style.

    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # In this case we can return a `matplotlib` plot directly.
    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    xs = np.array([p.x for p in df.geometry])
    ys = np.array([p.y for p in df.geometry])

    # Load the projection.
    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(xs),
        'central_latitude': lambda df: np.mean(ys)
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    # Set extent.
    if extent:
        ax.set_extent(extent)
    else:
        ax.set_extent((np.min(xs), np.max(xs), np.min(ys), np.max(ys)))

    # Clean up patches.
    _lay_out_axes(ax)

    if clip is None:
        sns.kdeplot(pd.Series([p.x for p in df.geometry]), pd.Series([p.y for p in df.geometry]),
                    transform=ccrs.PlateCarree(), ax=ax, **kwargs)
    else:
        # TODO: Get clipping working...
        raise NotImplementedError("This feature has not yet been added.")
        # for geom in clip:
        #     to_clip = sns.kdeplot(pd.Series([p.x for p in df.geometry]), pd.Series([p.y for p in df.geometry]),
        #                           transform=ccrs.PlateCarree(), ax=ax, **kwargs)
        #     feature = ShapelyFeature([geom.convex_hull], ccrs.PlateCarree())
        #     # import descartes; feature = descartes.PolygonPatch(geom.convex_hull, facecolor='steelblue')
        #     # ax.add_feature(feature, facecolor='None', **kwargs)
        #     # feature = mpl.patches.Circle((.75,.75),radius=.25,fc='none')
        #     ax.add_patch(feature)
        #     to_clip.set_clip_path(feature)
    return ax


def sankey(*args, projection=None,
           start=None, end=None, path=ccrs.Geodetic(),
           hue=None, categorical=False, scheme=None, k=None, cmap='viridis', vmin=None, vmax=None,
           legend=False, legend_kwargs=None, legend_labels=None,
           extent=None, figsize=(8, 6), ax=None,
           scale=None, limits=(1, 5), scale_func=None, legend_values=None,
           **kwargs):
    """
    A geospatial Sankey diagram (flow map).

    Parameters
    ----------
    df : GeoDataFrame, optional.
        The data being plotted. Uniquely amongst ``geoplot`` functions, this parameter is optional&mdash;it is not
        needed if ``start`` and ``end`` (and ``hue``, if provided) are iterables.
    projection : geoplot.crs object instance, optional
        A geographic coordinate reference system projection. Must be an instance of an object in the ``geoplot.crs``
        module, e.g. ``geoplot.crs.PlateCarree()``. Refer to ``geoplot.crs`` for further object parameters.

        If this parameter is not specified this method will return an unprojected pure ``matplotlib`` version of the
        chart, as opposed to the ``cartopy`` based plot returned when a projection is present. This allows certain
        operations, like stacking ``geoplot`` plots with and amongst other plots, which are not possible when a
        projection is present.

        However, for the moment failing to specify a projection will raise a ``NotImplementedError``.
    start : str or iterable
        Linear starting points: either the name of a column in ``df`` or a self-contained iterable. This parameter is
        required.
    end : str or iterable
        Linear ending points: either the name of a column in ``df`` or a self-contained iterable. This parameter is
        required.
    path : geoplot.crs object instance or iterable, optional
        If this parameter is provided as an iterable, it is assumed to contain the lines that the user wishes to
        draw to connect the points. This is useful if one wishes to e.g. build their own line-bundles.

        If this parameter is provided as a projection, that projection will be used for determining how the line is
        plotted. This parameter defaults to ``ccrs.Geodetic()``, which means that the *true* (e.g. shortest path
        will be plotted (e.g. `great circle distance<https://en.wikipedia.org/wiki/Great-circle_distance>`_); any
        other choice will result in what the shortest path is in that projection instead.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The data column whose entries are being discretely colorized. May be passed in any of a number of flexible
        formats. Defaults to None, in which case no colormap will be applied at all.
    categorical : boolean, optional
        Whether the inputted ``hue`` is already a categorical variable or not. Defaults to False. Ignored if ``hue``
        is set to None or not specified.
    scheme : None or {"quartiles"|"quantiles"|"equal_interval"|"fisher_jenks"} (?), optional
        The PySAL scheme which will be used to determine categorical bins for the ``hue`` choropleth. If ``hue`` is
        left unspecified or set to None this variable is ignored.
    k : int, optional
        If ``hue`` is specified and ``categorical`` is False, this number, set to 5 by default, will determine how
        many bins will exist in the output visualization. If ``hue`` is left unspecified or set to None this
        variable is ignored.
    cmap : matplotlib color, optional
        The string representation for a matplotlib colormap to be applied to this dataset. ``hue`` must be non-empty
        for a colormap to be applied at all, so this parameter is ignored otherwise.
    vmin : float, optional
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value.
    vmax : float, optional
        A strict ceiling on the value associated with the "top" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value.
    scale : str or iterable, optional
        The data parameter against which the geometries will be scaled.
    limits : (min, max) tuple, optional
        The minimum and maximum limits against which the shape will be scaled.
    scale_func : unfunc, optional
        The default scaling function is a linear one. You can change the scaling function to whatever you want by
        specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
        maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.
    legend_values : list, optional
        This variable will only have an effect if the ``scale`` parameter is in use (e.g. size is a variable) and
        ``legend=True``. Equal intervals will be used for the "points" in the legend by default. However,
        particularly if your scale is non-linear, oftentimes this isn't what you want. If this variable is provided as
        well, the values included in the input will be used by the legend instead.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to
    legend_kwargs : dict, optional
        Keyword arguments to be passed to the ``matplotlib`` ``ax.legend`` method. For a list of possible arguments
        refer to `the matplotlib documentation
        <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the resultant plot.
        Defaults to (8, 6), the ``matplotlib`` default global.
    extent : None or (minx, maxx, miny, maxy), optional
        If this parameter is set to None (default) this method will calculate its own cartographic display region. If
        an extrema tuple is passed---useful if you want to focus on a particular area, for example, or exclude certain
        outliers---that input will be used instead.
    ax : GeoAxesSubplot instance, optional
        A ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance onto which this plot will be graphed, used for overplotting
        multiple plots on one chart. If this parameter is left undefined a new axis will be created and used
        instead. A valid axis subplot instance can be obtained by saving the output of a prior plot to a variable (
        ``ax`` is the convention for this) or by using the ``plt.gca()`` matplotlib convenience method.
    kwargs: dict, optional
        Keyword arguments to be passed to the ``ax.scatter`` method doing the plotting. For a list of possible
        arguments refer to `the matplotlib documentation
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------
    A `Sankey diagram <https://en.wikipedia.org/wiki/Sankey_diagram>`_ is a type of plot useful for visualizing flow
    through a network. Its most famous historical example is cartographic -
    `Minard's classic diagram of Napolean's invasion of Russia <https://upload.wikimedia.org/wikipedia/commons/2/29/Minard.png>`_.

    This plot type is unusual amongst ``geoplot`` types in that it is meant for *two* columns of geography,
    resulting in a slightly different API. A basic ``sankey`` specifies data, origins, and destinations.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as ccrs
        gplt.sankey(mock_data, start='origin', end='destination', projection=ccrs.PlateCarree())

    .. image:: ../figures/sankey/sankey-initial.png

    However, Sankey diagrams need additional geospatial context to be interpretable. In this case (and for the
    remainder of the examples) we will provide this by overlaying world geometry.

    .. code-block:: python

        ax = gplt.sankey(mock_data, start='origin', end='destination', projection=ccrs.PlateCarree())
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-geospatial-context.png

    This function is very ``seaborn``-like in that the usual ``df`` argument is optional. If geometries are provided
    as independent iterables it can be dropped.

    .. code-block:: python

        ax = gplt.sankey(projection=ccrs.PlateCarree(), start=network['from'], end=network['to'])
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-alternative-method-signature.png

    You may be wondering why the lines are curved. By default, the paths followed by the plot are the *actual*
    shortest paths between those two points, in the spherical sense. This is known as `great circle distance
    <https://en.wikipedia.org/wiki/Great-circle_distance>`_. We can see this more clearly if we temporarily switch
    to an ortographic projection.

    .. code-block:: python

        ax = gplt.sankey(projection=ccrs.Orthographic(), start=network['from'], end=network['to'],
                 extent=(-180, 180, -90, 90))
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-greatest-circle-distance.png

    Plot using a different distance metric, pass it as an argument to the ``path`` parameter. Awkwardly, ``cartopy``
    ``crs`` objects (*not* ``geoplot`` ones) are required.

    .. code-block:: python

        from cartopy.crs import PlateCarree
        ax = gplt.sankey(projection=ccrs.PlateCarree(), start=network['from'], end=network['to'],
                         path=PlateCarree())
        ax.set_global()
        ax.coastlines()


    .. image:: ../figures/sankey/sankey-distance-metric.png

    User-provided custom pathing, a planned future feature, is still a work in progress.

    The ``hue`` parameter colorizes paths based on data.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to', path=PlateCarree(),
                         hue='mock_variable')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-hue.png


    ``cmap`` changes the colormap.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-cmap.png

    ``legend`` adds a legend.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True)
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-legend.png

    Pass keyword arguments to the legend with ``legend_kwargs``. This is often necessary for positioning.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.4, 1.0)})
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-legend-kwargs.png

    Specify custom legend labels with ``legend_labels``.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)},
                         legend_labels=['Very Low', 'Low', 'Average', 'High', 'Very High'])
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-legend-labels.png

    Change the number of bins with ``k``.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)},
                         k=3)
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-k.png

    Change the binning sceme with ``scheme``.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)},
                         k=3, scheme='equal_interval')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-scheme.png

    Specify ``categorical=True`` to plot an already-categorical variable.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         hue='above_meridian', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.2, 1.0)},
                         categorical=True)
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-categorical.png

    ``scale`` can be used to enable ``linewidth`` as a visual variable.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         scale='mock_data',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.2, 1.0)},
                         color='lightblue')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-scale.png


    By default, the polygons will be scaled according to the data such that the minimum value is scaled by a factor of
    0.2 while the largest value is left unchanged. Adjust this using the ``limits`` parameter.

    .. code-block:: python

        ax = gplt.sankey(network, projection=ccrs.PlateCarree(),
                         start='from', end='to',
                         scale='mock_data', limits=(1, 3),
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.2, 1.0)},
                         color='lightblue')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-limits.png

    The default scaling function is a linear one. You can change the scaling function to whatever you want by
    specifying a ``scale_func`` input. This should be a factory function of two variables which, when given the
    maximum and minimum of the dataset, returns a scaling function which will be applied to the rest of the data.

    .. code-block:: python

        def trivial_scale(minval, maxval):
            def scalar(val):
                return 0.5
            return scalar

        gplt.cartogram(boroughs, scale='Population Density', projection=ccrs.AlbersEqualArea(),
                       limits=(0.5, 1), scale_func=trivial_scale)

    .. image:: ../figures/sankey/sankey-scale-func.png
    """

    # Validate df.
    if len(args) > 1:
        raise ValueError("Invalid input.")
    elif len(args) == 1:
        df = args[0]
    else:
        df = None  # bind the local name here; initialize in a bit.

    # Validate the rest of the input.
    if (start is None) or (end is None):
        raise ValueError("The 'start' and 'ending' parameters must both be specified.")
    if (isinstance(start, str) or isinstance(end, str)) and (df is None):
        raise ValueError("Invalid input.")
    if isinstance(start, str):
        start = df[start]
    else:
        start = gpd.GeoSeries(start)
    if isinstance(end, str):
        end = df[end]
    else:
        end = gpd.GeoSeries(end)

    # Load points.
    points = pd.concat([start, end])
    # Initialize the `df` variable with a projection dummy, if it has not been initialized already.
    if df is None:
        df = gpd.GeoDataFrame(geometry=points)

    # Initialize the figure.
    fig = plt.figure(figsize=figsize)

    # In this case we can return a `matplotlib` plot directly.
    # TODO: Implement this.
    if not projection:
        raise NotImplementedError

    xs = np.array([p.x for p in points])
    ys = np.array([p.y for p in points])

    # Load the projection.
    projection = projection.load(df, {
        'central_longitude': lambda df: np.mean(xs),
        'central_latitude': lambda df: np.mean(ys)
    })

    # Set up the axis.
    if not ax:
        ax = plt.subplot(111, projection=projection)

    if extent:
        ax.set_extent(extent)
    else:
        ax.set_extent((np.min(xs), np.max(xs), np.min(ys), np.max(ys)))

    # Generate colormaps.
    if hue:
        hue = _validate_hue(df, hue)
        categorical, k, scheme = _validate_buckets(categorical, k, scheme)
        cmap, categories, values = _discrete_colorize(categorical, hue, scheme, k, cmap, vmin, vmax)
        colors = [cmap.to_rgba(v) for v in values]

        if legend:
            _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
    else:
        colors = [None]*len(start)

    # Check if the ``scale`` parameter is filled, and use it to fill a ``values`` name.
    if scale:
        if isinstance(scale, str):
            scalar_values = df[scale]
        else:
            scalar_values = scale

        # Compute a scale function.
        dmin, dmax = np.min(scalar_values), np.max(scalar_values)
        if not scale_func:
            dslope = (limits[1] - limits[0]) / (dmax - dmin)
            dscale = lambda dval: limits[0] + dslope * (dval - dmin)
        else:
            dscale = scale_func(dmin, dmax)

        # Apply the scale function.
        scalar_multiples = np.array([dscale(d) for d in scalar_values])
        widths = scalar_multiples * 1

        # Draw a legend, if appropriate.
        if legend:
            _paint_carto_legend(ax, scalar_values, legend_values, legend_labels, dscale, legend_kwargs)
    else:
        widths = [1] * len(df)  # pyplot default

    # Clean up patches.
    _lay_out_axes(ax)

    # Allow overwriting visual arguments.
    if 'linestyle' in kwargs.keys():
        linestyle = kwargs['linestyle']; kwargs.pop('linestyle')
    else:
        linestyle = '-'
    if 'color' in kwargs.keys():
        colors = [kwargs['color']]*len(df); kwargs.pop('color')
    if 'linewidth' in kwargs.keys():
        widths = [kwargs['linewidth']]*len(df); kwargs.pop('linewidth')

    # Duck test plot. The first will work if a valid transformation is passed, the second will work with an iterable.
    try:
        for origin, destination, color, width in zip(start, end, colors, widths):
            ax.plot([origin.x, destination.x], [origin.y, destination.y], transform=path,
                    linestyle=linestyle, linewidth=width, color=color, **kwargs)
    except ValueError:
        for origin, destination, line, color, width in zip(start, end, path, colors, widths):
            feature = ShapelyFeature([line], ccrs.PlateCarree())
            ax.add_feature(feature, linestyle=linestyle, linewidth=width, facecolor=color, **kwargs)

    return ax

##################
# HELPER METHODS #
##################


def _get_envelopes_min_maxes(envelopes):
    """
    Returns the extrema of the inputted polygonal envelopes. Used for setting chart extent where appropriate. Note
    tha the ``Quadtree.bounds`` object property serves a similar role.

    Parameters
    ----------
    envelopes : GeoSeries
        The envelopes of the given geometries, as would be returned by e.g. ``data.geometry.envelope``.

    Returns
    -------
    (xmin, xmax, ymin, ymax) : tuple
        The data extrema.

    """
    xmin = np.min(envelopes.map(lambda linearring: np.min([linearring.coords[1][0],
                                                          linearring.coords[2][0],
                                                          linearring.coords[3][0],
                                                          linearring.coords[4][0]])))
    xmax = np.max(envelopes.map(lambda linearring: np.max([linearring.coords[1][0],
                                                          linearring.coords[2][0],
                                                          linearring.coords[3][0],
                                                          linearring.coords[4][0]])))
    ymin = np.min(envelopes.map(lambda linearring: np.min([linearring.coords[1][1],
                                                           linearring.coords[2][1],
                                                           linearring.coords[3][1],
                                                           linearring.coords[4][1]])))
    ymax = np.max(envelopes.map(lambda linearring: np.max([linearring.coords[1][1],
                                                           linearring.coords[2][1],
                                                           linearring.coords[3][1],
                                                           linearring.coords[4][1]])))
    return xmin, xmax, ymin, ymax


def _get_envelopes_centroid(envelopes):
    """
    Returns the centroid of an inputted geometry column. Not currently in use, as this is now handled by this
    library's CRS wrapper directly. Light wrapper over ``_get_envelopes_min_maxes``.

    Parameters
    ----------
    envelopes : GeoSeries
        The envelopes of the given geometries, as would be returned by e.g. ``data.geometry.envelope``.

    Returns
    -------
    (mean_x, mean_y) : tuple
        The data centroid.
    """
    xmin, xmax, ymin, ymax = _get_envelopes_min_maxes(envelopes)
    return np.mean(xmin, xmax), np.mean(ymin, ymax)


def _lay_out_axes(ax):
    """
    Cartopy enables a a transparent background patch and an "outline" patch by default. This short method simply
    hides these extraneous visual features.

    Parameters
    ----------
    ax : matplotlib.Axes instance
        The ``matplotlib.Axes`` instance being manipulated.

    Returns
    -------
    None
    """
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)


def _validate_hue(df, hue):
    """
    The top-level ``hue`` parameter present in most plot types accepts a variety of input types. This method
    condenses this variety into a single preferred format---an iterable---which is expected by all submethods working
    with the data downstream of it.

    Parameters
    ----------
    df : GeoDataFrame
        The full data input, from which standardized ``hue`` information may need to be extracted.
    hue : Series, GeoSeries, iterable, str
        The data column whose entries are being discretely colorized, as (loosely) passed by the top-level ``hue``
        variable.

    Returns
    -------
    hue : iterable
        The ``hue`` parameter input as an iterable.
    """
    if not hue:
        nongeom = set(df.columns) - {df.geometry.name}
        if len(nongeom) > 1:
            raise ValueError("Ambiguous input: no 'hue' parameter was specified and the inputted DataFrame has more "
                             "than one column of data.")
        else:
            hue = df[list(nongeom)[0]]
            return hue
    elif isinstance(hue, str):
        hue = df[hue]
        return hue
    else:
        return gpd.GeoSeries(hue)


def _continuous_colormap(hue, cmap, vmin, vmax):
    """
    Creates a continuous colormap.

    Parameters
    ----------
    hue : iterable
        The data column whose entries are being discretely colorized. Note that although top-level plotter ``hue``
        parameters ingest many argument signatures, not just iterables, they are all preprocessed to standardized
        iterables before this method is called.
    cmap : ``matplotlib.cm`` instance
        The `matplotlib` colormap instance which will be used to colorize the geometries.
    vmin : float
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value. The value for this variable is
        meant to be inherited from the top-level variable of the same name.
    vmax : float
        A strict ceiling on the value associated with the "top" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value. The value for this variable is
        meant to be inherited from the top-level variable of the same name.

    Returns
    -------
    cmap : ``mpl.cm.ScalarMappable`` instance
        A normalized scalar version of the input ``cmap`` which has been fitted to the data and inputs.
    """
    mn = min(hue) if vmin is None else vmin
    mx = max(hue) if vmax is None else vmax
    norm = mpl.colors.Normalize(vmin=mn, vmax=mx)
    return mpl.cm.ScalarMappable(norm=norm, cmap=cmap)


def _discrete_colorize(categorical, hue, scheme, k, cmap, vmin, vmax):
    """
    Creates a discrete colormap, either using an already-categorical data variable or by bucketing a non-categorical
    ordinal one. If a scheme is provided we compute a distribution for the given data. If one is not provided we
    assume that the input data is categorical.

    This code makes extensive use of ``geopandas`` choropleth facilities.

    Parameters
    ----------
    categorical : boolean
        Whether or not the input variable is already categorical.
    hue : iterable
        The data column whose entries are being discretely colorized. Note that although top-level plotter ``hue``
        parameters ingest many argument signatures, not just iterables, they are all preprocessed to standardized
        iterables before this method is called.
    scheme : str
        The PySAL binning scheme to be used for splitting data values (or rather, the the string representation
        thereof).
    k : int
        The number of bins which will be used. This parameter will be ignored if ``categorical`` is True. The default
        value should be 5---this should be set before this method is called.
    cmap : ``matplotlib.cm`` instance
        The `matplotlib` colormap instance which will be used to colorize the geometries. This colormap
        determines the spectrum; our algorithm determines the cuts.
    vmin : float
        A strict floor on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is below this level will all be colored by the same threshold value.
    vmax : float
        A strict cealing on the value associated with the "bottom" of the colormap spectrum. Data column entries whose
        value is above this level will all be colored by the same threshold value.

    Returns
    -------
    (cmap, categories, values) : tuple
        A tuple meant for assignment containing the values for various properties set by this method call.
    """
    if not categorical:
        binning = __pysal_choro(hue, scheme, k=k)
        values = binning.yb
        binedges = [binning.yb.min()] + binning.bins.tolist()
        categories = ['{0:.2f} - {1:.2f}'.format(binedges[i], binedges[i + 1])
                      for i in range(len(binedges) - 1)]
    else:
        categories = np.unique(hue)
        if len(categories) > 10:
            warnings.warn("Generating a choropleth using a categorical column with over 10 individual categories. "
                          "This is not recommended!")
        value_map = {v: i for i, v in enumerate(categories)}
        values = [value_map[d] for d in hue]
    cmap = norm_cmap(values, cmap, mpl.colors.Normalize, mpl.cm, vmin=vmin, vmax=vmax)
    return cmap, categories, values


def _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs):
    """
    Creates a legend and attaches it to the axis. Meant to be used when a ``legend=True`` parameter is passed.

    Parameters
    ----------
    ax : matplotlib.Axes instance
        The ``matplotlib.Axes`` instance on which a legend is being painted.
    categories : list
        A list of categories being plotted. May be either a list of int types or a list of unique entities in the
        data column (e.g. as generated via ``numpy.unique(data)``. This parameter is meant to be the same as that
        returned by the ``_discrete_colorize`` method.
    cmap : ``matplotlib.cm`` instance
        The `matplotlib` colormap instance which will be used to colorize the legend entries. This should be the
        same one used for colorizing the plot's geometries.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to the values.
    legend_kwargs : dict
        Keyword arguments which will be passed to the matplotlib legend instance on initialization. This parameter
        is provided to allow fine-tuning of legend placement at the top level of a plot method, as legends are very
        finicky.

    Returns
    -------
    None
    """
    patches = []
    for value, cat in enumerate(categories):
        patches.append(mpl.lines.Line2D([0], [0], linestyle="none",
                              marker="o",
                              markersize=10, markerfacecolor=cmap.to_rgba(value)))
    # I can't initialize legend_kwargs as an empty dict() by default because of Python's argument mutability quirks.
    # cf. http://docs.python-guide.org/en/latest/writing/gotchas/. Instead my default argument is None,
    # but that doesn't unpack correctly, necessitating setting and passing an empty dict here. Awkward...
    if not legend_kwargs: legend_kwargs = dict()

    # If we are given labels use those, if we are not just use the categories.
    if legend_labels:
        ax.legend(patches, legend_labels, numpoints=1, fancybox=True, **legend_kwargs)
    else:
        ax.legend(patches, categories, numpoints=1, fancybox=True, **legend_kwargs)


def _paint_colorbar_legend(ax, values, cmap, legend_kwargs):
    """
    Creates a legend and attaches it to the axis. Meant to be used when a ``legend=True`` parameter is passed.

    Parameters
    ----------
    ax : matplotlib.Axes instance
        The ``matplotlib.Axes`` instance on which a legend is being painted.
    values : list
        A list of values being plotted. May be either a list of int types or a list of unique entities in the
        data column (e.g. as generated via ``numpy.unique(data)``. This parameter is meant to be the same as that
        returned by the ``_discrete_colorize`` method.
    cmap : ``matplotlib.cm`` instance
        The `matplotlib` colormap instance which will be used to colorize the legend entries. This should be the
        same one used for colorizing the plot's geometries.
    legend_kwargs : dict
        Keyword arguments which will be passed to the matplotlib legend instance on initialization. This parameter
        is provided to allow fine-tuning of legend placement at the top level of a plot method, as legends are very
        finicky.

    Returns
    -------
    None.
    """
    if not legend_kwargs: legend_kwargs = dict()
    cmap.set_array(values)
    plt.gcf().colorbar(cmap, ax=ax, **legend_kwargs)


def _paint_carto_legend(ax, values, legend_values, legend_labels, scale_func, legend_kwargs):
    """
    Creates a legend and attaches it to the axis. Meant to be used when a ``legend=True`` parameter is passed.

    Parameters
    ----------
    ax : matplotlib.Axes instance
        The ``matplotlib.Axes`` instance on which a legend is being painted.
    values : list
        A list of values being plotted. May be either a list of int types or a list of unique entities in the
        data column (e.g. as generated via ``numpy.unique(data)``. This parameter is meant to be the same as that
        returned by the ``_discrete_colorize`` method.
    legend_values : list, optional
        If a legend is specified, equal intervals will be used for the "points" in the legend by default. However,
        particularly if your scale is non-linear, oftentimes this isn't what you want. If this variable is provided as
        well, the values included in the input will be used by the legend instead.
    legend_labels : list, optional
        If a legend is specified, this parameter can be used to control what names will be attached to
    scale_func : ufunc
        The scaling function being used.
    legend_kwargs : dict
        Keyword arguments which will be passed to the matplotlib legend instance on initialization. This parameter
        is provided to allow fine-tuning of legend placement at the top level of a plot method, as legends are very
        finicky.

    Returns
    -------
    None.
    """

    # Set up the legend values.
    if legend_values is not None:
        display_values = legend_values
    else:
        display_values = np.linspace(np.max(values), np.min(values), num=5)
    display_labels = legend_labels if (legend_labels is not None) else display_values

    # Paint patches.
    patches = []
    for value in display_values:
        patches.append(mpl.lines.Line2D([0], [0], linestyle="none",
                       marker="o",
                       markersize=(20*scale_func(value))**(1/2),
                       markerfacecolor='None'))
    if not legend_kwargs: legend_kwargs = dict()
    ax.legend(patches, display_labels, numpoints=1, fancybox=True, **legend_kwargs)


def _validate_buckets(categorical, k, scheme):
    """
    This method validates that the hue parameter is correctly specified. Valid inputs are:

        1. Both k and scheme are specified. In that case the user wants us to handle binning the data into k buckets
           ourselves, using the stated algorithm. We issue a warning if the specified k is greater than 10.
        2. k is left unspecified and scheme is specified. In that case the user wants us to handle binning the data
           into some default (k=5) number of buckets, using the stated algorithm.
        3. Both k and scheme are left unspecified. In that case the user wants us bucket the data variable using some
           default algorithm (Quantiles) into some default number of buckets (5).
        4. k is specified, but scheme is not. We choose to interpret this as meaning that the user wants us to handle
           bucketing the data into k buckets using the default (Quantiles) bucketing algorithm.
        5. categorical is True, and both k and scheme are False or left unspecified. In that case we do categorical.
        Invalid inputs are:
        6. categorical is True, and one of k or scheme are also specified. In this case we raise a ValueError as this
           input makes no sense.

    Parameters
    ----------
    categorical : boolean
        Whether or not the data values given in ``hue`` are already a categorical variable.

    k : int
        The number of categories to use. This variable has no effect if ``categorical`` is True, and will be set to 5
        by default if it is False and not already given.

    scheme : str
        The PySAL scheme that the variable will be categorized according to (or rather, a string representation
        thereof).

    Returns
    -------
    (categorical, k, scheme) : tuple
        A possibly modified input tuple meant for reassignment in place.
    """
    if categorical and (k or scheme):
        raise ValueError("Invalid input: categorical cannot be specified as True simultaneously with scheme or k "
                         "parameters")
    if not k:
        k = 5
    if k > 10:
        warnings.warn("Generating a choropleth using a categorical column with over 10 individual categories. "
                      "This is not recommended!")
    if not scheme:
        scheme = 'Quantiles'  # This trips it correctly later.
    return categorical, k, scheme


def __indices_inside(df, window):
    """
    Returns the indices of columns in a ``geopandas`` object located within a certain rectangular window. This helper
    method is not currently used, see the quad package instead.

    Parameters
    ----------
    df : GeoSeries or GeoDataFrame
        The ``geopandas`` object containing a ``geometry`` of interest.
    window : tuple
        The ``(min_x, max_x, min_y, max_y)`` rectangular lookup coordinates from which points will be returned.

    Returns
    -------
    The indices within `df` of points within `window`.
    """
    min_x, max_x, min_y, max_y = window
    points = df.geometry.centroid
    is_in = points.map(lambda point: (min_x < point.x < max_x) & (min_y < point.y < max_y))
    indices = is_in.values.nonzero()[0]
    return indices
