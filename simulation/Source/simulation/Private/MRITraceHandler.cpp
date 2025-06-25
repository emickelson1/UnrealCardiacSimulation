// Fill out your copyright notice in the Description page of Project Settings.


#include "MRITraceHandler.h"
#include <map>
#include "Algo/Reverse.h"
#include <iostream>

void UMRITraceHandler::MRIScan(
    const int32 sliceCount, 
    const int32 sliceSize, 
    const FVector& minBounds, 
    const FVector& maxBounds, 
    TArray<uint8>& slices, 
    TArray<uint8>& segmentations
)
{
    // Initialize increment values
	const float zIncrement = (maxBounds.Z - minBounds.Z) / sliceCount;
    const float xIncrement = (maxBounds.X - minBounds.X) / sliceSize;
    float scale = (maxBounds.Y - minBounds.Y) / sliceSize;

    // Define slices and segmentation array size
    slices.SetNum(sliceCount * sliceSize * sliceSize);
    segmentations.SetNum(sliceCount * sliceSize * sliceSize);

    // Initialize line trace parameters
    TArray<FHitResult> forwardHits;
    TArray<FHitResult> backwardHits;
    FVector start = minBounds;
    FVector end = minBounds;
    end.Y = maxBounds.Y;
    const FCollisionQueryParams collisionParams = FCollisionQueryParams(
        FName(TEXT("MRITrace")), 
        true, 
        nullptr // No owner
    );
    const FCollisionObjectQueryParams queryParams = FCollisionObjectQueryParams(
        ECC_WorldStatic | ECC_WorldDynamic // Trace against static and dynamic objects
    );


    // Create each slice by line tracing repetitively
    for (int32 sliceIndex = 0; sliceIndex < sliceCount; ++sliceIndex)
    {
        // Line trace at each X position
        for (int32 xIndex = 0; xIndex < sliceSize; ++xIndex){
            // Forward trace (get hits on forward faces of colliders)
            bool forwardTrace = GetWorld()->LineTraceMultiByObjectType(
                forwardHits,
                start,
                end,
                queryParams,
                collisionParams
            );

            // Log forward trace hit results
            UE_LOG(LogTemp, Log, TEXT("Forward trace at slice %d, xIndex %d: %s"), sliceIndex, xIndex, forwardTrace ? TEXT("Hit") : TEXT("Missed"));

            // // Draw line
            // DrawDebugLine(GetWorld(), start, end, FColor::Green, true, 5.0f, 0, 1.0f);

            // If the forward trace did not hit anything, skip to the next linetrace
            if (!forwardTrace) {
                start.X += xIncrement;
                end.X += xIncrement;
                continue;
            }

            // Log analyzing trace hit message
            UE_LOG(LogTemp, Log, TEXT("\tAnalyzing forward trace at slice %d, xIndex %d"), sliceIndex, xIndex);

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
            UE_LOG(LogTemp, Log, TEXT("\tFound %d backwards hit(s)"), backwardHits.Num());

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
                int32 startYIndex = forwardHit.Distance / scale;
                int32 endYIndex = backwardHit->Distance / scale;
                for (int32 yIndex = startYIndex; yIndex < endYIndex; ++yIndex) {
                    int32 index = (sliceIndex * sliceSize * sliceSize) + (xIndex * sliceSize) + yIndex;
                    if (index < slices.Num()) {
                        slices[index] = 255;
                        segmentations[index] = 255;
                    }
                }
            }

            // Increment x values for the next iteration
            forwardHits.Empty();
            backwardHits.Empty();
            start.X += xIncrement;
            end.X += xIncrement;
        }

        // Reset for the next iteration
        start.X = minBounds.X;
        end.X = minBounds.X;
        start.Z += zIncrement;
        end.Z += zIncrement;
    }
}
