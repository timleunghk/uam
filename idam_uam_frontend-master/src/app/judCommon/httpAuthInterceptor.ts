import { Injectable } from '@angular/core';

import {
    HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HttpXsrfTokenExtractor
} from '@angular/common/http';
import { Observable } from 'rxjs';

export class HttpAuthInterceptor implements HttpInterceptor {

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // throw new Error("Method not implemented.");
        // console.log('HELLO');
        // req = req.clone({withCredentials: true});
        return next.handle(req);
    }

}

@Injectable()
export class HttpXsrfInterceptor implements HttpInterceptor {

  constructor(private tokenExtractor: HttpXsrfTokenExtractor) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // const headerName = 'X-CSRFToken';
    const headerName = 'X-CSRFToken';
    const respHeaderName = 'X-CSRFToken';
    let token = this.tokenExtractor.getToken() as string;
    if (token !== null && !req.headers.has(headerName)) {
      req = req.clone({ headers: req.headers.set(respHeaderName, token) });
    }
    return next.handle(req);
  }
}