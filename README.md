# Rain and flood informed vehicle routing

This project aims to optimize rainfall travel routes, primarily targeting transportation authorities. It was developed as part of the challenge proposed by CEMADEN (National Center for Monitoring and Early Warning of Natural Disasters) in Brazil. The challenge focuses on dynamic routing policies that prioritize people's safety in their vehicles, considering high-resolution and real-time rainfall forecasts. The project utilizes techniques such as Nowcasting to provide accurate and frequently updated rainfall predictions. By incorporating information about rainfall into route planning, the system seeks to offer more reliable and efficient routes, reducing exposure to heavy rains and potential flooding. The project provides classes and functions to facilitate rainfall-aware route optimization, using precipitation estimates and street shapefile data.
## Authors

- [@Delg11](https://github.com/Delg11)
- [@tiagormacedo](https://github.com/tiagormacedo)

## Paper

We have prepared a paper that provides detailed information about this project and includes relevant study cases. The paper will be submitted to SBPO - 23 (Brazilian Symposium on Operations Research) for consideration. 

As soons as possible we will post it here.

## Example

This project is designed to allow users to perform a case study by setting a date between January 1st and March 31st and selecting a route in the city of São Paulo. This is called an experiment, and it uses rain data from Radar São Roque and flood data from [CGE-SP](https://www.cgesp.org/v3/). For example:

<p align="center">
  <img src="https://github.com/RPvMM-2023-S1/Rain-and-flood-informed-vehicle-routing-problem/assets/130193931/eee2b6a0-0717-45d6-a04f-e1c582c4b41e" alt="Graph showing precipitation intensity: greener means less and yellower means more rain.">
  <br>
  <em>Routes from (-23.5048°, -46.4152°) to (-23.4986°, -46.3864°) on January 4, 2019  <br>
(Greener means less and yellower means more rain.)</em>
</p>

By default, for the 4:20pm case, for example, the user should see the following information:
<p align="center">
  <img src="https://github.com/RPvMM-2023-S1/Rain-and-flood-informed-vehicle-routing-problem/assets/130193931/7f861f73-ab6a-4eb0-883a-7d802d2fd80b" alt="Table with output data">
  <br>
  <em>Information organized in a table for improved comprehension.</em>
</p>

## License

This project is licensed under the [CC-BY-NC-SA] license (Creative Commons Attribution-NonCommercial-ShareAlike license). By contributing to this project, you agree that your contributions will be subject to the same license.

We appreciate your interest in contributing to our project and look forward to your contributions! If you have any further questions or need assistance, please feel free to reach out to us through the issue tracker.
