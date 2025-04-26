"use client";

import React, { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"

export default function Home() {
  const [search, setSearch] = useState("")
  const [includeImages, setIncludeImages] = useState(false)
  const [includeVideos, setIncludeVideos] = useState(false)

  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Ctrl++</CardTitle>
        {/* <CardDescription>Ctrl+F and more.</CardDescription> */}
      </CardHeader>
      <CardContent>
        <form>
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="name">Search</Label>
              <Input
                id="name"
                placeholder="..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="images"
              checked={includeImages}
              onCheckedChange={(checked) => setIncludeImages(!!checked)}
            />
            <label
              htmlFor="images"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Include images
            </label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="videos"
              checked={includeVideos}
              onCheckedChange={(checked) => setIncludeVideos(!!checked)}
            />
            <label
              htmlFor="videos"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Include videos
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button>{"<"}</Button>
          <Button>{">"}</Button>
        </div>
      </CardFooter>
    </Card>
  )
}
