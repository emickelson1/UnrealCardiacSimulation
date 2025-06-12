// // Fill out your copyright notice in the Description page of Project Settings.


// #include "CTReconstruct.h"

// CTReconstruct::CTReconstruct()
// {
// }

// CTReconstruct::~CTReconstruct()
// {
// }

// void CTReconstruct::reconstruct(
//     const TArray<float>& intensities, 
//     const int sliceCount, 
//     const int rotationCount, 
//     const int detectorCount, 
//     const float fov, 
//     const float r
//     )
// {
//     // Geometric calculations
//     const int imageSize = 512;                                                  // Size of the output image (512x512)
//     const float resolution = imageSize / fov;                                   // Pixels per cm
//     const float gamma0 = -atan2(fov/2.0, r);                                    // angle, in radians, of the first ray
//     const float gammaIncrement = atan2(fov/2.0, r) * 2 / (detectorCount - 1);   // angle, in radians, between rays

//     // Loop through slices
//     for (int sliceIndex = 0; sliceIndex < sliceCount; ++sliceIndex)
//     {
//         // Initialize the sinogram
//         std::vector<std::vector<float>> sinogram(rotationCount, std::vector<float>(detectorCount));

//         for (int i = 0; i < numAngles; ++i) {
//             float lambda = 2 * PI * i / numAngles;
//             for (int j = 0; j < detectorCount; ++j) {
//                 float gamma = -gammaMax + j * dGamma;
//                 sinogram[i][j] = computeG(lambda, gamma, r, 256/imageSize);
//             }
//         }

//         // Filter/ramp the sinogram?

//         // Perform backprojection
//         for (int i = 0; i < numAngles; ++i) {
//             float lambda = 2 * PI * i / numAngles;
//             for (int j = 0; j < detectorCount; ++j) {
//                 float gamma = -gammaMax + j * dGamma;
//                 float g_val = computeG(lambda, gamma, r, 256/imageSize);
                
//                 // Backproject the value
//                 for (int k = 0; k < imageSize; ++k) {
//                     // Calculate pixel coordinates
//                     int x = int(k * resolution);
//                     int y = int(k * resolution);
                    
//                     // Update the pixel value
//                     outputImage[y][x] += g_val;
//                 }
//             }
//         }
//     }
// }    

// float CTReconstruct::computeG(float lambda, float gamma, float r, float dt)
// {
//     // Perform geometric calculations
//     float ax = cos(lambda) * r;     // Detector x-coordinate
//     float ay = sin(lambda) * r;     // Detector y-coordinate

//     float ewx = cos(lambda);        // Unit vector for source trajectory
//     float ewy = sin(lambda);        
//     float eux = -sin(lambda);       // Unit vector tangent to source trajectory
//     float euy = cos(lambda);
    
//     // Calculate G
//     const float dt = 256 / imageSize;   // # segments for integration
//     for (float t = 0.0f; t < 2 * r; t += dt) {
//         float x = ax + t * dirX;
//         float y = ay + t * dirY;
        
//         // Convert to pixel coordinates
//         int ix = int(x / resolution);
//         int iy = int(y / resolution);
//         if (ix < 0 || ix >= imageSize || iy < 0 || iy >= imageSize) 
//         {
//             // Skip out-of-bounds pixels
//             continue; 
//         }
//         else 
//         {
//             // Interpolate the pixel value (nearest-neighor)
//             g_val += intensities[iy * fov + ix] * dt;
//         }
//     }

//     return g_val;
// }