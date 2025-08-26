// Fill out your copyright notice in the Description page of Project Settings.


#include "MRITraceHandler.h"
#include <map>
#include "Algo/Reverse.h"
#include <iostream>
#include <cmath>
#include <cstdint>
#include "Math/UnrealMathUtility.h"

void UMRITraceHandler::MRIScan(
    const int32 countX,
    const int32 countY,
    const int32 countZ,
    const FVector& minBounds, 
    const FVector& maxBounds, 
    const float TE,
    const float TR,
    const float R1,
    const float Gd,
    TArray<uint8>& volume, 
    TArray<uint8>& segmentation
)
{
    // Ensure 'this' is still valid
    if (!IsValid(this))
    {
        UE_LOG(LogTemp, Error, TEXT("MRIScan called on invalid UMRITraceHandler"));
        return;
    }

    // Initialize increment values
    const float xScale = (maxBounds.X - minBounds.X) / countX;       // X is assigned a scale because it is determined as a function of distance between hits
    const float yIncrement = (maxBounds.Y - minBounds.Y) / countY;
	const float zIncrement = (maxBounds.Z - minBounds.Z) / countZ;

    // Define slices and segmentation array size
    volume.SetNum(countZ * countY * countX);
    segmentation.SetNum(countZ * countY * countX);
    UE_LOG(LogTemp, Warning, TEXT("The volume and segmentation consist of %i and %i uint32s, respectively."), volume.Num(), segmentation.Num());

    // Initialize line trace parameters
    TArray<FHitResult> forwardHits;
    TArray<FHitResult> backwardHits;
    FVector start = minBounds;
    FVector end = minBounds;
    end.X = maxBounds.X;
    const FCollisionQueryParams collisionParams = FCollisionQueryParams(FName(TEXT("MRITrace")), true, nullptr);
    const FCollisionObjectQueryParams queryParams = FCollisionObjectQueryParams(ECC_WorldStatic | ECC_WorldDynamic | ECC_PhysicsBody);
    

    // Check dimensions
    if (countX <= 0 || countY <= 0 || countZ <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("MRIScan: invalid grid size (%d, %d, %d)"),
            countX, countY, countZ);
        return;
    }

    // Example size validation if you expect preallocated arrays:
    int64 expectedSize = (int64)countX * countY * countZ;
    if (volume.Num() < expectedSize || segmentation.Num() < expectedSize)
    {
        UE_LOG(LogTemp, Error,
            TEXT("MRIScan: arrays too small, expected at least %lld elements"),
            expectedSize);
        return;
    }

    // Target for calls to MakePairs
    TArray<TPair<FHitResult*, FHitResult*>> outHitPairs;

    // Create each slice by line tracing repetitively
    for (int32 zIndex = 0; zIndex < countZ; ++zIndex)
    {
        // Line trace at each Y position
        for (int32 yIndex = 0; yIndex < countY; ++yIndex) {
            // Do line traces
            DoLineTrace(start, end, 1, queryParams, collisionParams, forwardHits, backwardHits);
            MakePairs(forwardHits, backwardHits, outHitPairs);

            // Iterate through paired hits and fill slices and segmentations
            for (TPair<FHitResult*, FHitResult*> pair : outHitPairs) {
                // Break pair
                const FHitResult* forwardHit = pair.Key;
                const FHitResult* backwardHit = pair.Value;
            
                // Fill slice indices between start and end
                int32 startXIndex = forwardHit->Location.X / xScale;
                int32 endXIndex = (backwardHit != nullptr) ? backwardHit->Location.X / xScale : countX;   // If no backward hit, go to the end of the slice
            
                for (int32 xIndex = startXIndex; xIndex < endXIndex; ++xIndex) {
                    int32 index = (countX * countY * zIndex) + (countY * yIndex) + xIndex;
                    if (index < volume.Num()) {
                        if (forwardHit->GetComponent() != nullptr) {
                            UMaterialInterface *materialInterface = forwardHit->GetComponent()->GetMaterial(0);
                            if (materialInterface == nullptr){
                                UE_LOG(LogTemp, Warning, TEXT("Material interface is not valid on component"));
                                continue;
                            }
                            if (UMaterialInstance *instance = Cast<UMaterialInstance>(materialInterface)) {
                                // Assign a voxel value based on parameters read from material instance
                                volume[index] = ComputeVoxelValue(
                                    instance,   // material (T1, T2)    [ms]
                                    TR,         // TR                   [ms]
                                    TE,         // TE                   [ms]
                                    20,         // spin angle           [deg]
                                    Gd,         // Gd                   
                                    R1,         // R1                   
                                    5.0,        // R2                   
                                    1.0         // M0                   
                                );
                                
                                // Assign a number based on cardiac chamber name
                                float segmentationIndexParam;
                                bool success = instance->GetScalarParameterValue(FName(TEXT("Segmentation Index")), segmentationIndexParam);
                                segmentation[index] = success ? std::round(segmentationIndexParam): -1;
                                if (success) {
                                    // UE_LOG(LogTemp, Warning, TEXT("Segmentation index %i: %f"), index, segmentationIndexParam)
                                } else {
                                    UE_LOG(LogTemp, Warning, TEXT("Failed to get seg index from material hit on %s"), *materialInterface->GetName());
                                }   
                                // delete materialInterface;
                                // delete instance;
                            }
                            else {
                                UE_LOG(LogTemp, Warning, TEXT("Material is not a UMaterialInstance: %s"), *materialInterface->GetName());
                            }
                        } else if (index % 100 == 0){
                            UE_LOG(LogTemp, Warning, TEXT("Component is null at index %d. Note that only indices divisible by 100 will be logged."), index);
                        }
                    }
                }
            }

            // Increment y values for the next iteration
            forwardHits.Empty();
            backwardHits.Empty();
            start.Y += yIncrement;
            end.Y += yIncrement;
        }

        // Reset for the next iteration
        start.Y = minBounds.Y;
        end.Y = minBounds.Y;
        start.Z += zIncrement;
        end.Z += zIncrement;
    }
}

// uint8 UMRITraceHandler::ComputeVoxelValue(
//     const UMaterialInstance *material,
//     const float TE, 
//     const float TR,
//     const float R1,
//     const float Gd
// ) 
// {
//     // Get material T1, T2
//     float T1, T2;
//     T1 = material->GetScalarParameterValue(FName(TEXT("T1")), T1);
//     T2 = material->GetScalarParameterValue(FName(TEXT("T2")), T2);

//     // Apply contrast agent adjustment
//     T1 = 1 / ((1 / T1) + (Gd * R1));

//     return static_cast<uint8>(255 * (1 - std::exp(-TR / T1)) * (std::exp(-TE / T2)));
// }


// Compute GRE pixel intensity
uint8 UMRITraceHandler::ComputeVoxelValue(
    const UMaterialInstance *material,  // T1, T2 [ms]
    double TR,              // repetition time [ms]
    double TE,              // echo time [ms]
    double alphaDeg,        // flip angle [degrees]
    double Gd,              // Gadolinium concentration [mM]
    double R1,              // Gd relaxivity T1 [1/(s*mM)]
    double R2,              // Gd relaxivity T2 [1/(s*mM)]
    double M0               // Proton density / scaling
)
{
    // Read T1, T2 from material
    float T1, T2;
    material->GetScalarParameterValue(FName(TEXT("T1")), T1);
    material->GetScalarParameterValue(FName(TEXT("T2")), T2);
    
    // Convert relaxivities to ms^-1 units
    double R1_ms = R1 / 1000.0;
    double R2_ms = R2 / 1000.0;

    // Apply Gd effects
    double T1a = 1.0 / (1.0 / T1 + R1_ms * Gd);
    double T2a = 1.0 / (1.0 / T2 + R2_ms * Gd);

    // Flip angle in radians
    double alpha = FMath::DegreesToRadians(alphaDeg);

    // Steady-state longitudinal magnetization for spoiled GRE
    double E1 = std::exp(-TR / T1a);
    double s = M0 * std::sin(alpha) * (1 - E1) / (1 - E1 * std::cos(alpha));

    // Include T2 decay during TE
    s *= std::exp(-TE / T2a);

    // Clamp to 0-255
    s = std::max(0.0, std::min(255.0, s * 255.0));

    return static_cast<uint8>(s);
}


bool UMRITraceHandler::DoLineTrace(
    const FVector& start, 
    const FVector& end, 
    const int substeps,
    const FCollisionObjectQueryParams& queryParams, 
    const FCollisionQueryParams& collisionParams,
    TArray<FHitResult>& accForwardHits,
    TArray<FHitResult>& accReverseHits
) 
{
    // Initialize forward and reverse hits
    TArray<FHitResult> forwardHits, reverseHits;

    // Perform line trace in forward direction
    bool forwardTrace = GetWorld()->LineTraceMultiByObjectType(forwardHits, start, end, queryParams, collisionParams);

    // // Draw a line from start to end for debugging purposes
    // // white: good, grey: bad (some missing components), black: bad (no components found), red: good (forward trace missed)
    // bool allComponentsFound = true, noComponentsFound = true;
    // for (const FHitResult& hit : forwardHits) { hit.GetComponent() == nullptr ? allComponentsFound = false : noComponentsFound = false; }
    // auto& color = allComponentsFound ? (noComponentsFound ? FColor::Red : FColor::White) : (noComponentsFound ? FColor::Black : FColor(128, 128, 128));
    // DrawDebugLine(GetWorld(), start, end, color, true, 5.0f, 0, 1.0f);

    // If the trace missed, return here.
    if (!forwardTrace) {
        return false;
    }

    // Perform line trace in reverse direction
    bool reverseTrace = GetWorld()->LineTraceMultiByObjectType(reverseHits, end, start, queryParams, collisionParams);
    if (!reverseTrace) {
        UE_LOG(LogTemp, Warning, TEXT("Reverse trace failed from %s to %s despite forward trace success."), *end.ToString(), *start.ToString());
        return false;
    }

    // If both traces were successful, accumulate the hits. Apply reverse boolean at this step if necessary.
    accForwardHits.Append(forwardHits);
    accReverseHits.Append(reverseHits);

    // Target for calls to MakePairs
    TArray<TPair<FHitResult*, FHitResult*>> outHitPairs;
    MakePairs(forwardHits, reverseHits, outHitPairs);

    // Recursive call to enable multiple collisions on the same component
    for (int32 i = 0; i < substeps; i++){
        for (const TPair<FHitResult*, FHitResult*>& pair : outHitPairs) {
            if (pair.Value == nullptr) { break; }
            FVector close = pair.Key->Location;
            FVector far = pair.Value->Location;
            FVector origin = close + ((i+1.0f) / (substeps + 1.0f)) * (far - close); // Get a point between the two hits, lerp by index

            // Do additional detail trace
            FHitResult addForwardHit, addReverseHit;
            bool addForwardTrace = DoAdditionalDetailTrace(origin, far, queryParams, collisionParams, addForwardHit);     // away from camera
            bool addReverseTrace = DoAdditionalDetailTrace(origin, close, queryParams, collisionParams, addReverseHit);   // towards camera
            if (addForwardTrace && addReverseTrace && (addForwardHit.Location - addReverseHit.Location).Size() >= 1){
                // If both additional traces were successful, accumulate the hits
                accForwardHits.Add(addForwardHit);
                accReverseHits.Add(addReverseHit);
            }
        }
    }

    forwardHits.Empty();
    reverseHits.Empty();

    return true;
}



bool UMRITraceHandler::DoAdditionalDetailTrace(
    const FVector& start, 
    const FVector& end, 
    const FCollisionObjectQueryParams& queryParams, 
    const FCollisionQueryParams& collisionParams,
    FHitResult& outHitResult
) 
{
    // Perform the line trace
    return GetWorld()->LineTraceSingleByObjectType(outHitResult, start, end, queryParams, collisionParams);
}


bool UMRITraceHandler::MakePairs(
    const TArray<FHitResult>& forwardHits,
    const TArray<FHitResult>& reverseHits,
    TArray<TPair<FHitResult*, FHitResult*>>& outHitPairs
){
    outHitPairs.Empty();

    for (int32 i = 0; i < forwardHits.Num(); ++i) {
        // Get forward hit
        const FHitResult *forwardHit = &forwardHits[i];

        // Error check on this forward hit
        if (forwardHit->GetComponent() == nullptr) {
            UE_LOG(LogTemp, Warning, TEXT("Forward hit has no component."));
            break;
        }

        FHitResult *bestMatch = nullptr;
        const UPrimitiveComponent* hitComponent = forwardHit->GetComponent();
        for (int32 j = 0; j < reverseHits.Num(); ++j) {
            // Get reverse hit
            const FHitResult *reverseHit = &reverseHits[j];

            // Error check on this reverse hit
            if (reverseHit->GetComponent() == nullptr) {
                UE_LOG(LogTemp, Warning, TEXT("Reverse hit has no component."));
                continue;
            }

            // If the reverse hit is not from the same component, skip it
            if (reverseHit->GetComponent() != hitComponent) { continue; }

            // If this is the first reverse hit, set it as the best match
            if (bestMatch == nullptr){
                bestMatch = const_cast<FHitResult*>(reverseHit);
                continue;
            }

            // Check if the reverse hit is already paired with another forward hit
            bool alreadyPaired = false;
            for (TPair<FHitResult*, FHitResult*> pair : outHitPairs) {
                if (pair.Value == reverseHit) {
                    // If the reverse hit is already paired, skip it
                    alreadyPaired = true;
                    break;
                }
            }
            if (alreadyPaired) { continue; }

            // If the reverse hit is closer than the current best match, update the best match
            if ((forwardHit->Location - reverseHit->Location).Size() < (forwardHit->Location - bestMatch->Location).Size()) {
                bestMatch = const_cast<FHitResult*>(reverseHit);
                continue;
            }
        }

        // Add pair to the array
        outHitPairs.Add(TPair<FHitResult*, FHitResult*>(const_cast<FHitResult*>(forwardHit), bestMatch));
    }

    if (outHitPairs.Num() != (forwardHits.Num() + reverseHits.Num()) / 2) {
        UE_LOG(LogTemp, Warning, TEXT("Hit pairs count (%d) does not match total hits count (%d, %d). This may indicate a problem with the line trace."), outHitPairs.Num(), forwardHits.Num(), reverseHits.Num());
    }

    return true;
}