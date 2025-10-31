"use server";

import { z } from "zod";


const GenerateMusicSchema = z.object({
  prompt: z.string().min(10, "Music description must be at least 10 characters"),
  duration: z.number().min(5).max(60).default(20),
  output_format: z.enum(["mp3", "wav", "flac"]).default("mp3"),
  model: z.enum(["stable-audio-2.5", "stable-audio-2"]).default("stable-audio-2.5"),
});

export async function generateMusicAction(values: z.infer<typeof GenerateMusicSchema>) {
    const validatedFields = GenerateMusicSchema.safeParse(values);

    if (!validatedFields.success) {
        return {
            success: false,
            error: "Invalid music generation parameters.",
        };
    }

    try {
        const apiKey = process.env.STABILITY_API_KEY;
        if (!apiKey) {
            return {
                success: false,
                error: "Stability AI API key not configured. Please contact support.",
            };
        }

        // const client = new StableAudio2Client({ apiKey });
        // const result = await client.textToAudio(validatedFields.data);
        const result = {Notimplemented: true, success: false, error: "Not implemented"};

        if (!result.success) {
            return {
                success: false,
                error: result.error || "Failed to generate music.",
            };
        }

        if (!result.Notimplemented) {
            return {
                success: false,
                error: "No audio data received from API.",
            };
        }

        const audioDataUri = `data:audio`;

        return {
            success: true,
            audioDataUri,
            duration: validatedFields.data.duration,
        };
    } catch (error) {
        console.error("Music generation error:", error);
        return {
            success: false,
            error: "Failed to generate music. Please try again.",
        };
    }
}
