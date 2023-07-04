# Rain and flood informed vehicle routing

In this project, we present a method for obtaining routes that avoid rain and floods in a city. To achieve this, we model a city’s road network as a weighted multigraph, use data on precipitation and flood occurrences, and employ well-known methods to solve the shortest path problem based on this data.

This work was developed by [Gabriel Delgado](https://github.com/Delg11) and [Tiago Macedo](https://github.com/tiagormacedo) as part of the 2023 Fall semester class [_Resolução de Problemas via Modelagem Matemática_ (Resolution of problems via mathematical modeling)](http://sites.google.com/view/model-matematica) at [Unifesp](https://www.unifesp.br/campus/sjc/).  It was supervised by [Prof. Leonardo Souza](https://www.researchgate.net/profile/Leonardo-Santos-2) (CEMADEN), [Prof. Luiz Leduíno Neto](https://sites.google.com/view/leduino/) (Unifesp) and [Prof. Horácio Yanasse](https://br.linkedin.com/in/horacio-yanasse-39289794?original_referer=https%3A%2F%2Fduckduckgo.com%2F) (Unifesp).

## Files

The file that contains the main `Python` code is `rainfall_routing.py`.  The requirements for running `rainfall_routing.py` are contained in the file `requirements.txt`, and the precipitation data that we used to validate our results are contained in the folder `radar_data`.

We also created a Notebook version of the main `Python` code, `rainfall_routing.ipynb`.  This notebook contains further details, comments and an example.  For convenience, we reproduce this example below.

To run the `Python` code, we have to fix the boundary coordinates of the region that we want to study and the grid spacing of the radar:

```python
lat0 = -23.7748
latoo = -23.2959
lon0 = -46.6807
lonoo = -46.3841
dlat = -0.0090014
dlon = 0.009957
```

In the example above, we chose a region within the metropolitan area of Sao Paulo and the grid spacing given by Radar Sao Roque.  Using this information, we can instantiate a `Grafo` class and a `Radar` class:

```python
sao_paulo = Grafo(lat0, latoo, lon0, lonoo)
sao_roque = Radar(lat0, lon0, dlat, dlon)
```

Next, we have to choose the origin, destination and initial time of a route:

```python
origin = (-23.536718, -46.589832)
destination = (-23.531962, -46.653599)
agora = Agora(2019, 1, 4, 15, 0)
```

In the example above, the origin and destination are two points in downtown Sao Paulo, and the initial time is 3pm on January 4th, 2019.  Using this information, we can instantiate an `Experiment` class:

```python
example = Experiment(origin, destination, agora, sao_paulo, sao_roque)
```

To finish the setup, we only need to define a weight function that our experiment will minimize.  Here are a few weight functions that can be used:

```python
# Only minimize the duration of the route
def time_no_rain (graph, edge, flooded_points, rains):
    return graph.edges[edge]['travel_time']

# Only minimize the total length of the route
def length_no_rain (graph, edge, flooded_points, rains):
    return graph.edges[edge]['length']

# Minimize the time, taking into account rain and flood
def proposed (graph, edge, flooded_points, rains):
    if is_flooded(graph, edge, flooded_points):
        return float('inf')
    else:
        return graph.edges[edge]['travel_time'] * (1 + rains[edge]/100)
```

Now that we have all these ingredients, we can run an `experiment` and its `analysis`:

```python
for f in [time_no_rain, length_no_rain, proposed]:

    # Run the experiment
    edges_rains = example.experiment(f)

    # Print the results
    example.analysis(edges_rains)
```

The output will be a message containing information about the total duration, total length and total amount of rain of the routes that minimize each one of the functions above:
```
time_no_rain
The total distance traveled was 7.827 km.
The travel time was 10 minutes and 30 seconds.
The rainfall along the path was: 0.000 mm.
length_no_rain
The total distance traveled was 7.724 km.
The travel time was 11 minutes and 7 seconds.
The rainfall along the path was: 0.000 mm.
proposed
The total distance traveled was 8.039 km.
The travel time was 10 minutes and 52 seconds.
The rainfall along the path was: 0.000 mm.
```

One can see the difference between the routes obtained in this specific example below:
![image](https://github-production-user-asset-6210df.s3.amazonaws.com/130193931/251002177-5af01116-dee2-4c9a-9347-d09507831bfd.png)
🟦  Optimizing time without considering rain;
🟩  Optimizing distance without considering rain;
🟥  Optimizing time considering rain



## Future work

**Adapt the weight function to different vehicle types.**
The functions that we chose as weight functions are deformations of the travel times by a linear factor given by the amount of rain that is predicted for each edge (see function `proposed` in `rainfall_routing.ipynb`).  This fucntion does not differentiate between different types of vehicles, such as motorcycles, cars and trucks.  In order to improve the proposed model, one could acknowledge the vehicle type and adapt the weight functions accordingly.

**Incorporate traffic data.**
Another aspect that our `proposed` weight function does not presently consider is real-time traffic conditions for estimating travel times. Incorporating data on traffic flow would significantly improve the accuracy of the model in avoiding rain and floods.

**Prediction of floods.**
For the practical deployment of this model, the ability to predict flooding events is crucial. The `proposed` weight function relies on historical flooding data. However, to effectively utilize this method in the future, it is necessary to predict flooding events in advance. A possible enhancement could involve integrating hydraulic models with a machine learning approach that utilizes recent rainfall data along with historical flooding information for training purposes.


### Bug Reports and Feature Requests

If you encounter any bugs or have ideas for new features, please submit them through our GitHub issue tracker.
## License

This project is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike license](https://raw.githubusercontent.com/RPvMM-2023-S1/Rain-and-flood-informed-vehicle-routing-problem/main/LICENCE).

We appreciate your interest in our project and look forward to hearing all of your suggestions! If you have any questions, please feel free to reach out to us.
