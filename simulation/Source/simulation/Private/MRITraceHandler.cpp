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
    TArray<int32>& volume, 
    TArray<int32>& segmentation
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
    const FCollisionQueryParams collisionParams = FCollisionQueryParams(
        FName(TEXT("MRITrace")), 
        true, 
        nullptr // No owner
    );
    const FCollisionObjectQueryParams queryParams = FCollisionObjectQueryParams(
        ECC_WorldStatic | ECC_WorldDynamic | ECC_PhysicsBody // Trace against static and dynamic objects
    );


    // Create each slice by line tracing repetitively
    for (int32 zIndex = 0; zIndex < countZ; ++zIndex)
    {
        // Line trace at each Y position
        for (int32 yIndex = 0; yIndex < countY; ++yIndex){
            // Forward trace (get hits on forward faces of colliders)
            bool forwardTrace = GetWorld()->LineTraceMultiByObjectType(
                forwardHits,
                start,
                end,
                queryParams,
                collisionParams
            );

            // Log forward trace hit results
            UE_LOG(LogTemp, Log, TEXT("Forward trace at slice %d, yIndex %d: %s"), zIndex, yIndex, forwardTrace ? TEXT("Hit") : TEXT("Missed"));

            // // Draw line
            // DrawDebugLine(GetWorld(), start, end, FColor::Green, true, 5.0f, 0, 1.0f);

            // If the forward trace did not hit anything, skip to the next linetrace
            if (!forwardTrace) {
                start.Y += yIncrement;
                end.Y += yIncrement;
                continue;
            }

            // Log analyzing trace hit message
            // UE_LOG(LogTemp, Log, TEXT("\tAnalyzing forward trace at slice %d, xIndex %d"), sliceIndex, xIndex);

            // Backward trace and reverse results (get hits on back faces of colliders))
            bool backwardTrace = GetWorld()->LineTraceMultiByObjectType(
                backwardHits,
                end,
                start,
                queryParams,
                collisionParams
            );
            Algo::Reverse(backwardHits);

            // Log backwards hits information
            // UE_LOG(LogTemp, Log, TEXT("\tFound %d backwards hit(s)"), backwardHits.Num());

            // Iterate through hit objects, use the distances between front and back hits to fill slices and segmentations
            for (FHitResult &forwardHit : forwardHits){
                // Find the object hit by this forward trace
                const AActor *hitObject = forwardHit.GetActor();

                // Find the corresponding backward hit, then remove it from the backward hits array
                FHitResult *backwardHit = nullptr;
                for (int32 i = 0; i < backwardHits.Num(); ++i) {
                    if (backwardHits[i].GetActor() == hitObject) {
                        backwardHit = &backwardHits[i];
                        backwardHits.RemoveAt(i);
                        break;
                    }
                }
                if (!backwardHit) {
                    UE_LOG(LogTemp, Log, TEXT("\tNull backwards hit"));
                    continue;
                }
                UE_LOG(LogTemp, Log, TEXT("\tPaired forward, backward hits:\n\t\t\t\t[Forward]  %s\n\t\t\t\t[Backward] %s"), *forwardHit.ToString(), *backwardHit->ToString());

                // Fill slice indices between start and end
                int32 startXIndex = forwardHit.Location.X / xScale;
                int32 endXIndex = backwardHit->Location.X / xScale;
                // UE_LOG(LogTemp, Log, TEXT("\tstartY, endY = (%d, %d)"), startYIndex, endYIndex);
                for (int32 xIndex = startXIndex; xIndex < endXIndex; ++xIndex) {
                    int32 index = (countX * countY * zIndex) + (countY * yIndex) + xIndex;
                    // UE_LOG(LogTemp, Log, TEXT("\tSet slices[%d] = 255"), index);
                    if (index < volume.Num()) {
                        UMaterialInterface *materialInterface = forwardHit.GetComponent()->GetMaterial(0);
                        if (UMaterialInstance *instance = Cast<UMaterialInstance>(materialInterface)) {
                            // Assign a voxel value based on parameters read from material instance
                            volume[index] = ComputeVoxelValue(instance, TE, TR, R1, Gd);
                            
                            // Assign a number based on cardiac chamber name
                            float segmentationIndexParam;
                            segmentationIndexParam = instance->GetScalarParameterValue(FName(TEXT("SegmentationIndex")), segmentationIndexParam);
                            segmentation[index] = (int) segmentationIndexParam;
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

int32 UMRITraceHandler::ComputeVoxelValue(
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

    return static_cast<int32>(4095 * (1 - std::exp(-TR / T1)) * (std::exp(-TE / T2)));
}