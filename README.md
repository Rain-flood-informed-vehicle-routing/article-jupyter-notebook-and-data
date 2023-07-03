# Rain and flood informed vehicle routing

In this project, we present a method for obtaining routes that avoid rain and floods in a city. To achieve this, we model a city’s road network as a weighted multigraph, use data on precipitation and flood occurrences, and employ well-known methods to solve the shortest path problem based on this data.

This work was developed by [Gabriel Delgado](https://github.com/Delg11) and [Tiago Macedo](https://github.com/tiagormacedo) as part of the 2023 Fall semester class [_Resolução de Problemas via Modelagem Matemática_ (Resolution of problems via mathematical modeling)](http://sites.google.com/view/model-matematica) at [Unifesp](https://www.unifesp.br/campus/sjc/).  It was supervised by [Prof. Leonardo Souza](https://www.researchgate.net/profile/Leonardo-Santos-2) (CEMADEN), [Prof. Luiz Leduíno Neto](https://sites.google.com/view/leduino/) (Unifesp) and [Prof. Horácio Yanasse](https://br.linkedin.com/in/horacio-yanasse-39289794?original_referer=https%3A%2F%2Fduckduckgo.com%2F) (Unifesp).

## Example

This project is designed to allow users to perform a case study by setting a date between January 1st and March 31st and selecting a route in the city of São Paulo. This is called an experiment, and it uses rain data from Radar São Roque and flood data from [CGE-SP](https://www.cgesp.org/v3/). For example:
<p align="center">
  <img src="https://user-images.githubusercontent.com/130193931/250635498-bbc15f9a-7245-450d-81a6-8b96f6b4327d.png" alt="Graph showing precipitation intensity: greener means less and yellower means more rain.">
  <br>
  <em>Routes from (-23.5048°, -46.4152°) to (-23.4986°, -46.3864°) on January 4, 2019  <br>
(Greener means less and yellower means more rain.)</em>
</p>

By default, for the 4:20pm case, for example, the user should see the following information:\
The total distance traveled was 4.509 km.\
The travel time was 5 minutes and 56 seconds.\
The rainfall along the path was: 52509.700 mm.\
The total distance traveled was 4.007 km.\
The travel time was 6 minutes and 34 seconds.\
The rainfall along the path was: 59595.900 mm.\
The total distance traveled was 4.603 km.\
The travel time was 6 minutes and 2 seconds.\
The rainfall along the path was: 49770.300 mm.

The first three lines provide information about the route optimized for time.\
The next three lines pertain to the route optimized for length.\
The final three lines describe the route optimized for travel time while avoiding rain. It can be changed to optimime total lenght while avoiding rain.

## License

This project is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike license.

We appreciate your interest in our project and look forward to hearing all of your suggestions! If you have any questions, please feel free to reach out to us.
