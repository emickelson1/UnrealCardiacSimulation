// Fill out your copyright notice in the Description page of Project Settings.


#include "MRITraceHandler.h"
#include <map>
#include "Algo/Reverse.h"
#include <iostream>

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
    // Initialize increment values
    const float xScale = (maxBounds.X - minBounds.X) / countX;       // X is assigned a scale because it is determined as a function of distance between hits
    const float yIncrement = (maxBounds.Y - minBounds.Y) / countY;
	const float zIncrement = (maxBounds.Z - minBounds.Z) / countZ;

    // Define slices and segmentation array size
    volume.SetNum(countZ * countY * countX);
    segmentation.SetNum(countZ * countY * countX);

    // Initialize line trace parameters
    TArray<FHitResult> forwardHits;
    TArray<FHitResult> backwardHits;
    FVector start = minBounds;
    FVector end = minBounds;
    end.X = maxBounds.X;
    const FCollisionQueryParams collisionParams = FCollisionQueryParams(FName(TEXT("MRITrace")), true, nullptr);
    const FCollisionObjectQueryParams queryParams = FCollisionObjectQueryParams(ECC_WorldStatic | ECC_WorldDynamic | ECC_PhysicsBody);
    
    // Create each slice by line tracing repetitively
    for (int32 zIndex = 0; zIndex < countZ; ++zIndex)
    {
        // Line trace at each Y position
        for (int32 yIndex = 0; yIndex < countY; ++yIndex) {
            // // Draw line
            // DrawDebugLine(GetWorld(), start, end, FColor::Green, true, 5.0f, 0, 1.0f);

            // Do line traces
            DoLineTrace(start, end, 1, queryParams, collisionParams, forwardHits, backwardHits);
            const TArray<TPair<FHitResult*, FHitResult*>> hitPairs = MakePairs(forwardHits, backwardHits);

            // Iterate through paired hits and fill slices and segmentations
            for (TPair<FHitResult*, FHitResult*> pair : hitPairs) {
                // Break pair
                const FHitResult* forwardHit = pair.Key;
                const FHitResult* backwardHit = pair.Value;
                
                // Log hit results
                // UE_LOG(LogTemp, Log, TEXT("\tPaired forward, backward hits:\n\t\t\t\t[Forward]  %s\n\t\t\t\t[Backward] %s"), *forwardHit->ToString(), *backwardHit->ToString());

                // Fill slice indices between start and end
                int32 startXIndex = forwardHit->Location.X / xScale;
                int32 endXIndex = backwardHit != nullptr ? backwardHit->Location.X / xScale : countX;   // If no backward hit, go to the end of the slice
                
                // UE_LOG(LogTemp, Log, TEXT("\tstartY, endY = (%d, %d)"), startYIndex, endYIndex);
                for (int32 xIndex = startXIndex; xIndex < endXIndex; ++xIndex) {
                    int32 index = (countX * countY * zIndex) + (countY * yIndex) + xIndex;
                    // UE_LOG(LogTemp, Log, TEXT("\tSet slices[%d] = 255"), index);
                    if (index < volume.Num()) {
                        UMaterialInterface *materialInterface = forwardHit->GetComponent()->GetMaterial(0);
                        if (UMaterialInstance *instance = Cast<UMaterialInstance>(materialInterface)) {
                            // Assign a voxel value based on parameters read from material instance
                            volume[index] = ComputeVoxelValue(instance, TE, TR, R1, Gd);

                            // Assign a number based on cardiac chamber name
                            float segmentationIndexParam;
                            bool success = instance->GetScalarParameterValue(FName(TEXT("Segmentation Index")), segmentationIndexParam);
                            segmentation[index] = success ? std::round(segmentationIndexParam): -1;
                        }
                        else {
                            UE_LOG(LogTemp, Warning, TEXT("Material is not a UMaterialInstance: %s"), *materialInterface->GetName());
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

uint8 UMRITraceHandler::ComputeVoxelValue(
    const UMaterialInstance *material,
    const float TE, 
    const float TR,
    const float R1,
    const float Gd
) 
{
    // Get material T1, T2
    float T1, T2;
    T1 = material->GetScalarParameterValue(FName(TEXT("T1")), T1);
    T2 = material->GetScalarParameterValue(FName(TEXT("T2")), T2);

    // Apply contrast agent adjustment
    T1 = 1 / ((1 / T1) + (Gd * R1));

    return static_cast<uint8>(255 * (1 - std::exp(-TR / T1)) * (std::exp(-TE / T2)));
}

bool UMRITraceHandler::DoLineTrace(
    const FVector& start, 
    const FVector& end, 
    const int substeps,
    const FCollisionObjectQueryParams& queryParams, 
    const FCollisionQueryParams& collisionParams,
    TArray<FHitResult>& accForwardHits,
    TArray<FHitResult>& accReverseHits
){
    // Break recursion if substeps < 0
    if (substeps < 0) {
        return false;
    }

    // Initialize forward and reverse hits
    TArray<FHitResult> forwardHits;
    TArray<FHitResult> reverseHits;

    // Perform line trace in forward direction
    bool forwardTrace = GetWorld()->LineTraceMultiByObjectType(forwardHits, start, end, queryParams, collisionParams);
    if (!forwardTrace) {
        return false;
    }

    // Perform line trace in reverse direction
    bool reverseTrace = GetWorld()->LineTraceMultiByObjectType(reverseHits, end, start, queryParams, collisionParams);

    if ((forwardHit.Location() - reverseTrace.Location()).Size() < 1){
        return false;
    }

    // If both traces were successful, accumulate the hits
    accForwardHits.Append(forwardHits);
    accReverseHits.Append(reverseHits);

    // Recursive call to enable multiple collisions on the same component
    if (substeps > 0) {
        for (TPair<FHitResult*, FHitResult*> pair : MakePairs(forwardHits, reverseHits)) {
            if (pair.Value == nullptr) { break; }
            FVector forward = pair.Key->Location;
            FVector reverse = pair.Value->Location;
            FVector center = (forward + reverse) / 2.0f;
            DoLineTrace(center, forward, substeps - 1, queryParams, collisionParams, accForwardHits, accReverseHits);
            DoLineTrace(reverse, center, substeps - 1, queryParams, collisionParams, accReverseHits, accForwardHits);
        }
    }

    return true;
}

TArray<TPair<FHitResult*, FHitResult*>> UMRITraceHandler::MakePairs(
    const TArray<FHitResult>& forwardHits,
    const TArray<FHitResult>& reverseHits
){
    TArray<TPair<FHitResult*, FHitResult*>> hitPairs;

    for (FHitResult forwardHit : forwardHits) {
        FHitResult* bestMatch = nullptr;
        const UPrimitiveComponent* hitComponent = forwardHit.GetComponent();

        // Find the corresponding reverse hit
        for (FHitResult reverseHit : reverseHits) {
            // If the reverse hit is not from the same component, skip it
            if (reverseHit.GetComponent() != hitComponent) { continue; }
            
            // If this is the first reverse hit, set it as the best match
            if (bestMatch == nullptr){
                bestMatch = &reverseHit;
                continue;
            }

            // Check if the reverse hit is already paired with another forward hit
            bool alreadyPaired = false;
            for (TPair<FHitResult*, FHitResult*> pair : hitPairs) {
                if (pair.Value == &reverseHit) {
                    // If the reverse hit is already paired, skip it
                    alreadyPaired = true;
                }
            }
            if (alreadyPaired) { continue; }

            // If the reverse hit is closer than the current best match, update the best match
            if ((forwardHit.Location - reverseHit.Location).Size() < (forwardHit.Location - bestMatch->Location).Size()) {
                bestMatch = &reverseHit;
                continue;
            }
        }

        // Add pair to the array
        hitPairs.Add(TPair<FHitResult*, FHitResult*>(&forwardHit, bestMatch));
    }

    return hitPairs;
}